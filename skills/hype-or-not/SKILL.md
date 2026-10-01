---
name: hype-or-not
description: >-
  Upstream triage shield and reality-check engine for AI workflows. Critically evaluates incoming links, articles, YouTube videos, GitHub repos, newsletters, and social media drop-offs for technical substance vs. empty hype, AI slop density, and system alignment before entering testing queues or internal workflows. Automatically logs triage assessments to local CSV/Markdown or Google Sheets. Triggers on: 'hype or not', 'reality check', 'triage link', 'slop audit', 'audit newsletter', 'triage drop-off', 'is this hype', 'evaluate tool', 'hype check', 'triage incoming'.
license: MIT
version: 1.0.0
---

# Hype or Not: Upstream Triage Shield & Reality-Check Engine

Upstream Guardian and Reality-Check Shield for developers, researchers, and AI agents. Protects engineering workflows from internet noise, marketing clickbait, fraud, unedited AI slop, and empty hype by enforcing a strict two-phase evaluation pipeline before any candidate tool, framework, or idea reaches testing queues, architecture notes, or production workflows.

---

## When to Use

Activate this skill whenever the user or system asks to:
- Audit, filter, or reality-check incoming links, GitHub repos, social media posts, newsletters, blogs, or drop-offs.
- Shield the workspace from empty hype, influencer engagement-bait, AI slop, or fraudulent capability claims.
- Determine whether a substantive tool or concept aligns with project architecture, policies, cost limits, and token economics.
- Log triage results into a structured ledger (local CSV, Markdown table, JSONL, or Google Sheet).

---

## Two-Phase Triage Architecture

Every candidate passes through a strict sequential two-phase gate:

```
[ Incoming Content / Link / Tool Candidate ]
                     │
                     ▼
┌───────────────────────────────────────────────┐
│     PHASE 1: Reality, Slop & Substance        │
│  - Anti-Slop Audit (20 writing anti-patterns) │
│  - Primary Source Grounding (repo/code/docs)  │
│  Is it real technical signal, or empty hype?  │
└───────────────────────┬───────────────────────┘
                        │
             ┌──────────┴──────────┐
             │                     │
    [ EMPTY HYPE / SLOP ]    [ SUBSTANTIVE ]
             │                     │
             ▼                     ▼
        RULE OUT        ┌───────────────────────────────────────────────┐
       (Hard Stop:      │       PHASE 2: Architecture & Policy Gate     │
     save attention     │  - Cost & SaaS Gate (low cost vs. paywall)    │
       and tokens)      │  - Token Economy Gate (no runaway loops)      │
                        │  - Parity & Privacy Gate (local/open data)    │
                        │  Is it architecturally aligned with project?  │
                        └───────────────────────┬───────────────────────┘
                                                │
                                     ┌──────────┴──────────┐
                                     │                     │
                               [ MISALIGNED ]         [ ALIGNED ]
                                     │                     │
                                     ▼                     ▼
                                 RULE OUT          PROMOTE TO QUEUE
                             (Policy Failure)      (or STUDY / DEFER)
```

---

## Phase 1: Reality, Slop & Substance Filter

Determine whether there is genuine, reproducible engineering substance, or whether the candidate is promotional noise, unedited AI slop, or fabricated influencer claims.

### 1. Anti-Slop & Pattern Audit
Evaluate candidate text against the [Slop Heuristics Taxonomy](./references/slop_heuristics.md):
- **Forbidden Structural Tells:** Em dash addiction (`—` or `--`) used as stylistic filler.
- **Generic Openings:** *"In today's fast-paced digital landscape...", "Delve into the revolutionary..."*
- **Hollow Superlatives:** *"Game-changer", "testament to", "paradigm shift", "beacon of innovation", "seamlessly", "effortlessly"*.
- **Statistical Burstiness:** Monotonous, unvarying sentence lengths ($CV < 0.25$) indicate unedited machine generation.
- **Run the Automated Evaluator:**
  ```bash
  python ./scripts/evaluate.py --text "Paste candidate text here"
  # Or evaluate a file/README directly:
  python ./scripts/evaluate.py path/to/README.md
  ```

### 2. Primary Source Grounding
Never trust secondary summaries, newsletter digests, or viral X/LinkedIn promotional threads.
- Inspect the primary source directly: official GitHub repository, release notes, commit velocity, open issue tracker, or academic paper.
- Verify whether the code actually exists, runs locally, has an open-source license, or is merely a conceptual landing page or closed waitlist.

### 3. The Hard Stop Rule
If Phase 1 fails (`Verdict = EMPTY HYPE`), assign `RULE OUT` immediately.
**Evaluation terminates here.** Never waste time, human attention, or token context evaluating architecture alignment for ungrounded junk.

---

## Phase 2: Architecture & Policy Gate

If (and ONLY if) Phase 1 demonstrates genuine substance, evaluate the candidate against the project's policy gates (configurable via `config.yaml`):

1. **Cost & SaaS Gate:** Reject tools requiring expensive recurring SaaS subscriptions or proprietary enterprise cloud lock-in. Prefer local CLI tools, open-source libraries, or native workspace integrations.
2. **Token Economy Gate:** Reject autonomous loops that run indefinitely and burn API tokens without verifiable progress. Enforce bounded short-chain execution and prompt cache awareness.
3. **Parity & Privacy Gate:** Ensure data is stored in inspectable, human-and-machine-readable formats (plain text Markdown, CSV, JSON, SQLite). Reject tools that lock data behind opaque proprietary formats or attempt unmonitored human lockout.
4. **Compliance & Licensing Gate:** Reject tools requiring ToS-violating browser scrapers or credential harvesting. Verify compatible open-source licenses (MIT, Apache 2.0, BSD).

---

## Standard Triage Taxonomies

### Phase 1 Verdicts (Technical Reality)
- `SUBSTANTIVE`: Demonstrable code, verified architecture, or reproducible empirical evidence.
- `PARTIAL HYPE`: Valid technical kernel or worthwhile concept, but wrapped in inflated claims, selective benchmarks, or marketing fluff.
- `EMPTY HYPE`: Fabricated claims, fake metrics, unedited promotional slop, affiliate bait, or non-functional vapourware.

### Phase 2 Alignment (System Fit)
- `ALIGNED`: Fully compliant with project cost, token economy, privacy, and architecture policies.
- `MISALIGNED`: Violates core constraints (e.g. expensive paywall, runaway token burn, proprietary lock-in, ToS violation).
- `N/A (Reference)`: Substantive content belonging to a specialized external domain rather than primary software/AI architecture.

### Agent Recommendations (Triage Actions)
- `PROMOTE TO INTAKE QUEUE [Focus Area]`: Substantive and aligned; approved for live testing and deployment.
- `STUDY [Specific Focus]`: Substantive concepts, architecture patterns, or empirical studies worth absorbing without adopting the tool.
- `DEFER [Explicit Trigger]`: Substantive, but placed on hold until a specific milestone, project thread, or dependency activates.
- `RULE OUT [Specific Reason]`: Terminated due to Phase 1 empty hype/slop or Phase 2 policy failure (e.g. `RULE OUT: SaaS paywall violates Low-Cost principle`).

### Priority Rankings
- `P1 (High)`: Urgent architectural or operational relevance. Directly unlocks current roadmap goals or saves substantial cost.
- `P2 (Medium)`: High strategic value; worth scheduled implementation or study.
- `P3 (Low)`: Minor tactical value, interesting niche reference, or background context.
- `N/A`: Ruled out or external reference.

---

## Logging Results

Log every evaluated candidate using the universal storage adapter [append_triage.py](./scripts/append_triage.py):

### Default: Local CSV (Zero-Setup)
```bash
python ./scripts/append_triage.py \
  --title "Tool or Article Name" \
  --url "https://github.com/example/repo" \
  --verdict "SUBSTANTIVE" \
  --alignment "ALIGNED" \
  --recommendation "PROMOTE TO INTAKE QUEUE [Prompt Caching]" \
  --priority "P1 (High)" \
  --impact "Reduces token consumption by 40% via prompt caching." \
  --summary "Clean open-source library with verified benchmarks and MIT license."
```

### Local Markdown Table
```bash
python ./scripts/append_triage.py --backend markdown --output-file ./TRIAGE.md ...
```

### Google Sheets (Optional)
```bash
python ./scripts/append_triage.py --backend gsheet --spreadsheet-id "<YOUR_SHEET_ID>" ...
```

---

## Critical Invariants

1. **Evidence Over Claim:** Never classify a tool as `SUBSTANTIVE` based purely on social media posts, demo videos, or influencer hype. Always verify against primary code or docs.
2. **Never Evaluate Alignment on Pure Slop:** If an item fails Phase 1, stop immediately. Do not burn tokens explaining why junk fails system principles.
3. **Good Does Not Equal Aligned:** A technically impressive tool that costs \$500/month or runs unmonitored infinite loops may still be ruled out in Phase 2.
4. **Strict Anti-Slop Discipline:** Triage summaries must adhere to clean prose: zero em dashes, zero hollow superlatives, active voice, high signal-to-token ratio.
