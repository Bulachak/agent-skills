#!/usr/bin/env python3
"""
append_triage.py - Universal Storage Adapter for Hype-or-Not Triage.
Supports appending triage records to:
  1. Local CSV (default)
  2. Local Markdown table
  3. Local JSON Lines (JSONL)
  4. Google Sheets (via Google Workspace CLI `gws` if installed and configured)

Automatically strips newsletter tracking parameters, referral codes, and
subscriber reaction JWTs from `--url` before writing, and refuses to log
accidental unsubscribe/account-action links.

Zero mandatory third-party dependencies (pure standard library).
"""

import argparse
import base64
import csv
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse

DEFAULT_CSV_PATH = "triage_log.csv"
DEFAULT_MD_PATH = "triage_log.md"
DEFAULT_JSONL_PATH = "triage_log.jsonl"

CSV_HEADERS = [
    "Timestamp",
    "Title",
    "Source URL",
    "Phase 1 Verdict",
    "Phase 2 Alignment",
    "Agent Recommendation",
    "Priority",
    "Impact Assessment",
    "Triage Summary & Strategic Rationale",
]

STRIP_QUERY_KEYS_LOWER = {
    "token",
    "access_token",
    "auth_token",
    "id_token",
    "jwt",
    "sig",
    "signature",
    "r",
    "publication_id",
    "post_id",
    "isfreemail",
    "triedredirect",
    "just_signed_up",
    "referrer_token",
    "freesignupemail",
    "mc_cid",
    "mc_eid",
    "mkt_tok",
    "_hsenc",
    "_hsmi",
    "vero_id",
    "vero_conv",
    "oly_enc_id",
    "oly_anon_id",
    "fbclid",
    "gclid",
    "dclid",
    "msclkid",
    "twclid",
    "igshid",
    "si",
}

FORBIDDEN_URL_PATH_PATTERNS = (
    "/action/disable_email",
    "/unsubscribe",
)


def _unwrap_substack_redirect(url: str) -> str:
    """Unwrap https://substack.com/redirect/2/<base64url-payload>.<sig> without network I/O."""
    m = re.match(r"^https?://(?:www\.)?substack\.com/redirect/2/([A-Za-z0-9_-]+)(?:\.[A-Za-z0-9_-]+)?", url)
    if not m:
        return url
    b64_part = m.group(1)
    pad = "=" * ((4 - len(b64_part) % 4) % 4)
    try:
        decoded = base64.urlsafe_b64decode(b64_part + pad).decode("utf-8", errors="strict")
        payload = json.loads(decoded)
        target = payload.get("e")
        if isinstance(target, str) and target.startswith(("http://", "https://")):
            return target
    except Exception:
        return url
    return url


def sanitize_source_url(raw_url: str) -> str:
    """Strip newsletter tracking, referral codes, and subscriber reaction JWTs from source URLs."""
    if not raw_url:
        return ""
    candidate = _unwrap_substack_redirect(raw_url.strip())
    parsed = urllib.parse.urlsplit(candidate)
    if parsed.scheme not in ("http", "https"):
        return candidate

    lower_path = parsed.path.lower()
    for bad in FORBIDDEN_URL_PATH_PATTERNS:
        if bad in lower_path:
            raise ValueError(f"Refusing to log an email unsubscribe or account-action URL: {parsed.netloc}{parsed.path}")

    if not parsed.query:
        return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", parsed.fragment))

    kept_params = []
    for k, v in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True):
        kl = k.lower()
        if (
            kl in STRIP_QUERY_KEYS_LOWER
            or kl.startswith("utm_")
            or "token" in kl
            or "secret" in kl
            or "unsubscribe" in kl
        ):
            continue
        kept_params.append((k, v))

    clean_query = urllib.parse.urlencode(kept_params, doseq=True)
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, clean_query, parsed.fragment))


def run_self_test() -> int:
    substack_raw = (
        "https://example.substack.com/p/example-post"
        "?utm_source=post-email-title&publication_id=11111&post_id=22222"
        "&utm_campaign=email-post-title&isFreemail=false"
        "&token=INERT_TEST_FIXTURE_JWT_DO_NOT_USE"
        "&r=inert01&triedRedirect=true&utm_medium=email"
    )
    assert sanitize_source_url(substack_raw) == "https://example.substack.com/p/example-post"

    yt_raw = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s&si=share_track_id&utm_source=newsletter"
    assert sanitize_source_url(yt_raw) == "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s"

    gsheet_raw = "https://docs.google.com/spreadsheets/d/EXAMPLE_SHEET_ID/edit?gid=0#gid=0"
    assert sanitize_source_url(gsheet_raw) == gsheet_raw

    wrapped_payload = base64.urlsafe_b64encode(
        json.dumps({"e": substack_raw, "p": 22222, "s": 11111}).encode("utf-8")
    ).decode("ascii").rstrip("=")
    wrapped_url = f"https://substack.com/redirect/2/{wrapped_payload}.INERT_SIG?"
    assert sanitize_source_url(wrapped_url) == "https://example.substack.com/p/example-post"

    blocked_caught = False
    try:
        test_unsub_url = "https://example.invalid" + "/action/disable" + "_email"
        sanitize_source_url(test_unsub_url)
    except ValueError:
        blocked_caught = True
    assert blocked_caught, "Expected ValueError on disable_email action URL"

    print("[PASS] append_triage.py --self-test: 5/5 URL sanitization assertions passed.")
    return 0


def append_to_csv(filepath, row, dry_run=False):
    """Append a row to a local CSV file, creating headers if the file does not exist."""
    if dry_run:
        print(f"[DRY-RUN] Would append to CSV: {filepath}")
        print(json.dumps(dict(zip(CSV_HEADERS, row)), indent=2))
        return

    file_exists = os.path.isfile(filepath) and os.path.getsize(filepath) > 0
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True) if os.path.dirname(filepath) else None

    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(CSV_HEADERS)
        writer.writerow(row)
    print(f"[OK] Appended triage entry to CSV: {filepath}")


def append_to_markdown(filepath, row, dry_run=False):
    """Append a row to a Markdown table in a local file."""
    if dry_run:
        print(f"[DRY-RUN] Would append to Markdown table: {filepath}")
        return

    file_exists = os.path.isfile(filepath) and os.path.getsize(filepath) > 0
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True) if os.path.dirname(filepath) else None

    clean_row = [str(col).replace("|", "\\|").replace("\n", " ").strip() for col in row]
    table_line = "| " + " | ".join(clean_row) + " |\n"

    with open(filepath, "a", encoding="utf-8") as f:
        if not file_exists:
            header_line = "| " + " | ".join(CSV_HEADERS) + " |\n"
            separator_line = "| " + " | ".join(["---"] * len(CSV_HEADERS)) + " |\n"
            f.write("# Hype-or-Not Triage Log\n\n")
            f.write(header_line)
            f.write(separator_line)
        f.write(table_line)
    print(f"[OK] Appended triage entry to Markdown: {filepath}")


def append_to_jsonl(filepath, row, dry_run=False):
    """Append an entry to a JSON Lines file."""
    record = dict(zip(CSV_HEADERS, row))
    if dry_run:
        print(f"[DRY-RUN] Would append to JSONL: {filepath}")
        print(json.dumps(record, indent=2))
        return

    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True) if os.path.dirname(filepath) else None
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"[OK] Appended triage entry to JSONL: {filepath}")


def append_to_gsheet(spreadsheet_id, range_name, row, dry_run=False):
    """Append to a Google Sheet using the Google Workspace CLI (gws)."""
    gws_bin = shutil.which("gws") or shutil.which("gws.exe")
    if not gws_bin:
        fallback = os.path.expanduser(r"~/.local/bin/gws.exe")
        if os.path.isfile(fallback):
            gws_bin = fallback

    if not gws_bin:
        print("ERROR: Google Workspace CLI (`gws`) not found in PATH or ~/.local/bin.", file=sys.stderr)
        print("Install gws or switch to '--backend csv' or '--backend markdown'.", file=sys.stderr)
        sys.exit(1)

    params = {
        "spreadsheetId": spreadsheet_id,
        "range": range_name,
        "valueInputOption": "USER_ENTERED",
    }
    body = {"values": [row]}

    cmd = [
        gws_bin,
        "sheets",
        "spreadsheets",
        "values",
        "append",
        "--params",
        json.dumps(params),
        "--json",
        json.dumps(body),
    ]

    if dry_run:
        cmd.append("--dry-run")

    res = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        print(f"ERROR: gws command failed with exit code {res.returncode}", file=sys.stderr)
        print(res.stderr, file=sys.stderr)
        sys.exit(res.returncode)

    print(res.stdout)
    if not dry_run:
        print(f"[OK] Appended row to Google Sheet ID: {spreadsheet_id}")


def main():
    parser = argparse.ArgumentParser(
        description="Universal triage storage adapter for Hype-or-Not skill."
    )
    parser.add_argument("--title", help="Candidate title / clean name")
    parser.add_argument("--url", default="", help="Original source URL or repository link (auto-sanitized)")
    parser.add_argument(
        "--verdict",
        choices=["SUBSTANTIVE", "PARTIAL HYPE", "EMPTY HYPE"],
        help="Phase 1 Technical Reality Verdict",
    )
    parser.add_argument(
        "--alignment",
        choices=["ALIGNED", "MISALIGNED", "N/A (Reference)"],
        help="Phase 2 System / Policy Alignment",
    )
    parser.add_argument("--recommendation", help="Actionable recommendation (e.g. PROMOTE, STUDY, RULE OUT)")
    parser.add_argument(
        "--priority",
        choices=["P1 (High)", "P2 (Medium)", "P3 (Low)", "N/A"],
        default="P3 (Low)",
        help="Priority classification",
    )
    parser.add_argument("--impact", default="", help="1-2 sentence operational impact assessment")
    parser.add_argument("--summary", default="", help="Crisp triage summary & strategic rationale")
    parser.add_argument("--timestamp", help="Timestamp (YYYY-MM-DD HH:MM:SS), defaults to current time")

    parser.add_argument(
        "--backend",
        choices=["csv", "markdown", "jsonl", "gsheet"],
        default="csv",
        help="Storage destination (default: csv)",
    )
    parser.add_argument("--output-file", help="Custom output file path for csv, markdown, or jsonl")
    parser.add_argument("--spreadsheet-id", help="Google Spreadsheet ID (required for --backend gsheet)")
    parser.add_argument("--sheet-range", default="'Hype or Not Note Triage'!A:L", help="Google Sheet tab and range")

    parser.add_argument("--json-file", help="Path to JSON file containing entry fields")
    parser.add_argument("--dry-run", action="store_true", help="Simulate write without modifying storage")
    parser.add_argument(
        "--self-test", action="store_true", help="Run deterministic URL-sanitization self-tests and exit"
    )

    args = parser.parse_args()
    if args.self_test:
        sys.exit(run_self_test())

    if args.json_file:
        with open(args.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        title = data.get("title", "")
        raw_url = data.get("url", "")
        verdict = data.get("verdict", "")
        alignment = data.get("alignment", "")
        recommendation = data.get("recommendation", "")
        priority = data.get("priority", "P3 (Low)")
        impact = data.get("impact", "")
        summary = data.get("summary", "")
        timestamp = data.get("timestamp", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        backend = data.get("backend", args.backend)
        spreadsheet_id = data.get("spreadsheet_id", args.spreadsheet_id)
        sheet_range = data.get("sheet_range", args.sheet_range)
    else:
        if not (args.title and args.verdict and args.recommendation):
            parser.error("At minimum, --title, --verdict, and --recommendation are required.")
        title = args.title
        raw_url = args.url
        verdict = args.verdict
        alignment = args.alignment or ("ALIGNED" if verdict == "SUBSTANTIVE" else "MISALIGNED")
        recommendation = args.recommendation
        priority = args.priority
        impact = args.impact
        summary = args.summary
        timestamp = args.timestamp or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        backend = args.backend
        spreadsheet_id = args.spreadsheet_id
        sheet_range = args.sheet_range

    try:
        url = sanitize_source_url(raw_url)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)

    row = [
        timestamp,
        title,
        url,
        verdict,
        alignment,
        recommendation,
        priority,
        impact,
        summary,
    ]

    if backend == "csv":
        out_path = args.output_file or DEFAULT_CSV_PATH
        append_to_csv(out_path, row, dry_run=args.dry_run)
    elif backend == "markdown":
        out_path = args.output_file or DEFAULT_MD_PATH
        append_to_markdown(out_path, row, dry_run=args.dry_run)
    elif backend == "jsonl":
        out_path = args.output_file or DEFAULT_JSONL_PATH
        append_to_jsonl(out_path, row, dry_run=args.dry_run)
    elif backend == "gsheet":
        if not spreadsheet_id:
            print("ERROR: --spreadsheet-id is required when using --backend gsheet.", file=sys.stderr)
            sys.exit(1)
        append_to_gsheet(spreadsheet_id, sheet_range, row, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
