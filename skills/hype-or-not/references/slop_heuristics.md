# Slop Heuristics & Hype Detection Taxonomy

This reference provides objective criteria for identifying unedited AI-generated copy, influencer hype, and marketing vapourware during **Phase 1: Reality, Slop & Substance Filtering**.

---

## 1. The 20 AI Writing Anti-Patterns

When reviewing articles, newsletters, social media threads, and product documentation, check against these common indicators of automated, low-substance generation:

1. **Em Dash Addiction:** Heavy reliance on em dashes (`—` or `--`) as decorative structural bridges instead of concise sentence punctuation (periods, commas, colons).
2. **Generic Corporate Openings:** Opening with empty atmospheric framing:
   - *"In today's fast-paced digital landscape..."*
   - *"As artificial intelligence continues to evolve..."*
   - *"Delve into the revolutionary world of..."*
3. **Hollow Superlatives:** Elevating ordinary utilities into historic milestones:
   - *"Game-changer"*, *"testament to"*, *"beacon of innovation"*, *"paradigm shift"*, *"tapestry"*, *"synergy"*.
4. **Superfluous Adverbs:** Empty modifiers that mask a lack of technical detail:
   - *"Seamlessly integrates"*, *"effortlessly scales"*, *"robustly handles"*, *"pivotal development"*.
5. **Passive Voice Obfuscation:** Hiding the actor or mechanism to sound authoritative without providing technical proof:
   - *"It is widely recognized that..."* instead of naming the actual benchmark or author.
6. **Over-Hedging & False Caution:** Passive non-committal hedging:
   - *"It is worth noting that..."*, *"Arguably, one might consider..."*, *"Potentially transformative..."*.
7. **Decorative Formatting Sprawl:** Gratuitous decorative emojis at the start of every bullet point, unnecessary divider lines, or artificial callout blocks containing no real substance.
8. **Repetitive Concluding Summaries:** Closing short notes with generic summaries:
   - *"In conclusion, by embracing these transformative methodologies, teams can navigate..."*
9. **Artificial Structural Symmetry:** Forcing bullet points or paragraphs into identical sentence lengths and identical grammatical structures regardless of underlying technical facts.
10. **Call-to-Action Fluff:** Generic engagement-bait wrap-ups:
    - *"The future is here. Are you ready to level up your workflow?"*
11. **Meta-Language Inflation:** Writing about the document rather than the technical subject:
    - *"This article aims to provide a comprehensive exploration into..."*
12. **Vague Quantifiers:** Masking absent empirical metrics:
    - *"A wide variety of benchmarks demonstrate significant improvements..."* (without naming the dataset, baseline, or margin).
13. **Inflated Vocabulary Sprawl:** Using ornate academic jargon where direct, simple words communicate the engineering fact faster.
14. **Performative Enthusiasm:** Unjustified exclamation marks and cheerleader adjectives in technical software documentation.
15. **Redundant Synonyms:** Pairing identical adjectives for emotional weight:
    - *"Vital and essential"*, *"core and fundamental"*, *"powerful and robust"*.
16. **Prompt Echoing:** Paraphrasing the original user query or popular headline back to the reader as the first paragraph.
17. **Superficial Present-Participle Analysis:** Paragraphs filled with superficial *-ing* clauses:
    - *"Highlighting the intersection of technology and design, demonstrating the importance of efficiency..."*
18. **Fabricated Unit Economics:** Guru math that multiplies theoretical maximums to project effortless revenue:
    - *"10 clients x $5k/mo = $50k/mo automated profit with zero overhead."*
19. **Contextual Amnesia Fillers:** Re-explaining basic definitions (e.g. defining what an LLM or an API is) inside specialized technical guides.
20. **Ungrounded Speculation:** Stating capability claims as existing facts without verifiable code, live repositories, or reproducible benchmarks.

---

## 2. Statistical Signal Pass (Burstiness & Cadence)

### Sentence Length Burstiness (Coefficient of Variation)
Human writers vary sentence rhythm naturally—combining punchy 3-word assertions with longer compound explanations. LLMs trained on standard alignment tend toward uniform, mid-length sentences.

$$\text{Burstiness CV} = \frac{\sigma}{\mu}$$

- **High Burstiness ($CV > 0.45$):** Natural human cadence. Dynamic sentence variance.
- **Low Burstiness ($CV < 0.25$):** Flat, monotonous sentence rhythm. Strong indicator of unedited machine output.

### Slop Density Score (0 to 100)
- **0–30 (High Substance):** Code snippets, verifiable commit histories, reproduction commands, bounded claims.
- **31–70 (Partial Hype):** Real underlying tool or model, but wrapped in promotional language, selective benchmarks, or unverified performance claims.
- **71–100 (Empty Hype / Slop):** Marketing landing page with zero public code, heavy use of anti-patterns 1–20, fabricated revenue models, or vapourware waitlists.

---

## 3. Primary Source Grounding Checklist

Before assigning any Phase 1 Verdict, verify these four primary dimensions:

1. **Repository Existence & Health:**
   - Does a public repository exist under an approved license (MIT, Apache 2.0, etc.)?
   - Are there recent commits from multiple contributors, or was the repository abandoned shortly after an announcement thread?
   - Are open issues being addressed, or are basic install bugs ignored?
2. **Reproducibility:**
   - Does the README contain functional installation instructions (`pip install`, `npm install`, `docker run`)?
   - Can the tool be run locally or via API with documented authentication?
3. **Benchmark Verification:**
   - Are performance numbers compared against established baselines (e.g. SWE-bench, HumanEval, MMLU, standard latency profiles)?
   - Were evaluations run across standard test sets or hand-picked cherry-picked examples?
4. **Commercial Transparency:**
   - Is the project genuinely open-source, or is it an open-core funnel designed to force an immediate enterprise upgrade?
   - Are API pricing and recurring subscription costs documented transparently?
