#!/usr/bin/env python3
"""
append_triage.py - Universal Storage Adapter for Hype-or-Not Triage.
Supports appending triage records to:
  1. Local CSV (default)
  2. Local Markdown table
  3. Local JSON Lines (JSONL)
  4. Google Sheets (via Google Workspace CLI `gws` if installed and configured)

Zero mandatory third-party dependencies (pure standard library).
"""

import argparse
import csv
import datetime
import json
import os
import shutil
import subprocess
import sys

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

    # Escape pipes in content
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
        # Check standard user local bin path on Windows
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
    parser.add_argument("--url", default="", help="Original source URL or repository link")
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

    args = parser.parse_args()

    # Load from JSON file if provided
    if args.json_file:
        with open(args.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        title = data.get("title", "")
        url = data.get("url", "")
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
        url = args.url
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
