#!/usr/bin/env python3
"""
evaluate.py - Standalone Slop Density & Technical Reality Evaluator.
Analyzes text, Markdown documents, or repository READMEs for:
  - Sentence length burstiness (Coefficient of Variation)
  - Em dash density
  - Known AI writing anti-patterns and marketing fluff
  - Overall Slop Density Score (0-100) and suggested Phase 1 Verdict

Pure Python standard library (no pip packages required).
"""

import argparse
import math
import re
import sys

# High-frequency AI writing anti-patterns & buzzwords
SLOP_PATTERNS = [
    r"\bgame[- ]changer\b",
    r"\btestament to\b",
    r"\bbeacon of\b",
    r"\bparadigm shift\b",
    r"\btapestry\b",
    r"\bsynerg(y|ies|istic)\b",
    r"\bseamlessly\b",
    r"\beffortlessly\b",
    r"\brobustly\b",
    r"\bpivotal\b",
    r"\bdelve into\b",
    r"\bin today's fast[- ]paced\b",
    r"\bit is crucial to note\b",
    r"\bit is worth noting\b",
    r"\bunlock(ing)? the power of\b",
    r"\barguably\b",
    r"\brevolutioniz(e|ing|ed)\b",
    r"\btransformative\b",
    r"\bgroundbreaking\b",
    r"\bunleash(ing)?\b",
    r"\bnavigat(e|ing) the (complexities|landscape)\b",
    r"\bholistic approach\b",
    r"\bcutting[- ]edge\b",
    r"\bstate[- ]of[- ]the[- ]art\b",
]


def split_sentences(text):
    """Clean and split text into sentences."""
    clean = re.sub(r"```[\s\S]*?```", "", text)  # remove code blocks
    clean = re.sub(r"https?://\S+", "", clean)   # remove URLs
    clean = re.sub(r"#+.*", "", clean)           # remove markdown headings
    sentences = re.split(r"(?<=[.!?])\s+", clean)
    return [s.strip() for s in sentences if len(s.strip().split()) >= 3]


def compute_burstiness(sentences):
    """Compute sentence length burstiness (Coefficient of Variation = std / mean)."""
    if not sentences:
        return 0.0, 0.0, 0.0
    lengths = [len(s.split()) for s in sentences]
    mean = sum(lengths) / len(lengths)
    if mean == 0:
        return 0.0, 0.0, 0.0
    variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
    std = math.sqrt(variance)
    cv = std / mean
    return cv, mean, std


def audit_text(text):
    """Run full slop and substance audit on input text."""
    word_count = len(text.split())
    if word_count == 0:
        return {"error": "Empty text provided"}

    # Em dash count
    em_dash_count = text.count("—") + text.count(" -- ")
    em_dash_per_100 = (em_dash_count / (word_count / 100.0)) if word_count >= 100 else em_dash_count

    # Buzzword & slop match count
    matched_patterns = {}
    total_pattern_matches = 0
    for pattern in SLOP_PATTERNS:
        matches = len(re.findall(pattern, text, re.IGNORECASE))
        if matches > 0:
            clean_name = pattern.replace(r"\b", "").replace(r"[- ]", " ")
            matched_patterns[clean_name] = matches
            total_pattern_matches += matches

    # Sentence burstiness
    sentences = split_sentences(text)
    cv, mean_len, _ = compute_burstiness(sentences)

    # Technical markers (code blocks, CLI commands, imports, config)
    code_block_count = len(re.findall(r"```", text)) // 2
    technical_terms = len(re.findall(r"\b(git|docker|npm|pip|api|http|json|sqlite|curl|sdk|cli|python|rust)\b", text, re.IGNORECASE))

    # Compute Slop Density Score (0 - 100)
    # Penalties:
    # 1. Low burstiness (< 0.35) adds up to 30 points
    # 2. Pattern density (buzzwords per 100 words) adds up to 40 points
    # 3. High em dash density adds up to 20 points
    # Rewards:
    # 1. Code blocks and technical terms reduce slop score by up to 30 points

    burstiness_penalty = 0.0
    if cv < 0.25:
        burstiness_penalty = 30.0
    elif cv < 0.40:
        burstiness_penalty = 15.0

    pattern_density = (total_pattern_matches / (word_count / 100.0)) if word_count >= 100 else total_pattern_matches
    pattern_penalty = min(pattern_density * 15.0, 40.0)

    em_dash_penalty = min(em_dash_per_100 * 5.0, 20.0)

    technical_credit = min((code_block_count * 5.0) + (technical_terms * 1.5), 30.0)

    raw_score = 20.0 + burstiness_penalty + pattern_penalty + em_dash_penalty - technical_credit
    slop_score = max(0.0, min(100.0, raw_score))

    # Suggested Phase 1 Verdict
    if slop_score <= 35.0 and (code_block_count > 0 or technical_terms > 5):
        verdict = "SUBSTANTIVE"
    elif slop_score <= 65.0:
        verdict = "PARTIAL HYPE"
    else:
        verdict = "EMPTY HYPE"

    return {
        "word_count": word_count,
        "sentence_count": len(sentences),
        "mean_sentence_length": round(mean_len, 1),
        "burstiness_cv": round(cv, 3),
        "em_dash_count": em_dash_count,
        "slop_pattern_matches": total_pattern_matches,
        "matched_fluff": matched_patterns,
        "code_blocks": code_block_count,
        "technical_terms": technical_terms,
        "slop_density_score": round(slop_score, 1),
        "suggested_verdict": verdict,
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate text for AI slop density and technical substance.")
    parser.add_argument("file", nargs="?", help="Path to text or markdown file to evaluate")
    parser.add_argument("--text", help="Direct text string to evaluate")

    args = parser.parse_args()

    if args.text:
        content = args.text
    elif args.file:
        with open(args.file, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    elif not sys.stdin.isatty():
        content = sys.stdin.read()
    else:
        parser.error("Please supply a file path, --text, or piped stdin.")

    results = audit_text(content)

    print("=" * 60)
    print(" HYPE-OR-NOT TECHNICAL SUBSTANCE & SLOP AUDIT")
    print("=" * 60)
    print(f" Total Words:           {results['word_count']}")
    print(f" Total Sentences:       {results['sentence_count']} (avg {results['mean_sentence_length']} words/sentence)")
    print(f" Burstiness (CV):       {results['burstiness_cv']} ({'Dynamic/Human' if results['burstiness_cv'] >= 0.45 else 'Monotonous/AI-like'})")
    print(f" Em Dash Count:         {results['em_dash_count']}")
    print(f" Marketing Buzzwords:   {results['slop_pattern_matches']}")
    if results['matched_fluff']:
        print("   Matched terms:       " + ", ".join(f"{k} ({v})" for k, v in results['matched_fluff'].items()))
    print(f" Code Blocks:           {results['code_blocks']}")
    print(f" Technical Markers:     {results['technical_terms']}")
    print("-" * 60)
    print(f" Slop Density Score:    {results['slop_density_score']} / 100")
    print(f" Suggested Verdict:     {results['suggested_verdict']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
