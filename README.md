# Agent Skills by Bulachak

Production-grade, battle-tested agent skills for autonomous AI coding assistants and engineering agents. 

Designed for **Google Antigravity**, **Claude Code**, **Cursor**, **Windsurf**, **Codex**, and modern open agent runtimes.

---

## What are Agent Skills?

An **Agent Skill** is a modular package of domain knowledge, deterministic runbooks, evaluation heuristics, and executable tools that teach an AI agent how to reliably perform complex workflows.

Each skill is structured according to the open **Progressive Disclosure** agent specification:
- **`SKILL.md` (Mandatory):** Core instruction file with standardized YAML frontmatter (`name`, `description`). The agent reads only the name and description into its top-level context, loading the full procedure only when the workflow activates.
- **`scripts/` (Optional):** Executable helpers, parsers, and command runners (Python/Bash) that turn complex tasks into deterministic single-command executions.
- **`references/` (Optional):** In-depth specifications, taxonomies, and manuals referenced on demand to minimize prompt token burn.
- **`templates/` (Optional):** Reusable starter configs, schemas, and file scaffolds.

---

## Skill Catalog

| Skill | Status | Category | Description |
| :--- | :--- | :--- | :--- |
| [**`hype-or-not`**](./skills/hype-or-not/) | `Stable v1.0.0` | Triage & Quality Shield | Upstream triage shield and reality-check engine. Critically evaluates incoming links, articles, repos, and drop-offs for technical substance, AI slop density, and system alignment before entering testing queues. Logs to local CSV/Markdown or Google Sheets. |

---

## Universal Installation Guide

Different AI coding assistants look for skills in different locations. Choose your runtime below:

### 1. Google Antigravity

Antigravity natively discovers skills across both global and workspace configurations:

#### Option A: Global Installation (Available across all projects)
Clone or copy the skill into your user config directory:

- **Windows:** `%USERPROFILE%\.gemini\config\skills\<skill-name>`
- **macOS / Linux:** `~/.gemini/config/skills/<skill-name>`

```bash
# Example: Install hype-or-not globally
git clone https://github.com/Bulachak/agent-skills.git temp-skills
mkdir -p ~/.gemini/config/skills
cp -r temp-skills/skills/hype-or-not ~/.gemini/config/skills/
rm -rf temp-skills
```

#### Option B: Workspace / Project Installation (Shared with team via git)
Place the skill inside the `.agents/skills/` directory at the root of your project:

```bash
mkdir -p .agents/skills
cp -r /path/to/agent-skills/skills/hype-or-not .agents/skills/
```

---

### 2. Claude Code (Anthropic CLI)

Claude Code discovers skills placed in its global or project directory:

#### Option A: Global Installation
- **Windows:** `%USERPROFILE%\.claude\skills\<skill-name>`
- **macOS / Linux:** `~/.claude/skills/<skill-name>`

```bash
mkdir -p ~/.claude/skills
cp -r agent-skills/skills/hype-or-not ~/.claude/skills/
```

#### Option B: Zero-Drift Directory Junction / Symlink (Recommended)
If you maintain a local clone of `agent-skills`, link directly into your Claude Code runtime to keep updates synchronized:

```powershell
# Windows (PowerShell - Run as Administrator or Developer Mode):
New-Item -ItemType Junction -Path "$HOME\.claude\skills\hype-or-not" -Target "C:\path\to\agent-skills\skills\hype-or-not"
```

```bash
# macOS / Linux:
ln -s ~/path/to/agent-skills/skills/hype-or-not ~/.claude/skills/hype-or-not
```

---

### 3. Cursor

Cursor uses project-level rule files and instructions:

1. Copy the desired skill into `.cursor/skills/<skill-name>/` or your workspace root.
2. In your `.cursorrules` or `.cursor/rules/<rule-name>.mdc`, add a reference to the skill:
   ```markdown
   When auditing incoming links, GitHub repos, or tools for hype vs reality,
   activate and follow the instructions in:
   .cursor/skills/hype-or-not/SKILL.md
   ```

---

### 4. Windsurf (Codeium)

Windsurf supports workspace rules and scratchpad instructions:

1. Place the skill directory in `.windsurf/skills/<skill-name>/` or `.agents/skills/<skill-name>/`.
2. In your `.windsurfrules` file:
   ```markdown
   # Triage & Quality Protocol
   For evaluating tool candidates or external links, follow:
   .windsurf/skills/hype-or-not/SKILL.md
   ```

---

### 5. Codex / OpenAI Assistants / Generic CLI

For headless LLM harnesses or OpenAI assistant loops:

1. Mount or provide `SKILL.md` as part of the assistant's knowledge base or prompt directory.
2. Provide the scripts directory in the execution PATH so the model can invoke `python scripts/evaluate.py` and `python scripts/append_triage.py`.

---

## Core Engineering Principles

Every skill in this repository adheres to three non-negotiable standards:

1. **Progressive Disclosure:** Large reference manuals and scripts live in subdirectories. The main `SKILL.md` is kept lean to preserve model context windows.
2. **Zero-Dependency Core:** Evaluators and helper scripts use the standard Python library whenever possible. They run out-of-the-box on clean developer machines without fragile pip dependency chains.
3. **Anti-Slop Discipline:** Every skill enforces active voice, zero em-dash filler, reproducible benchmarks, and verifiable technical evidence over marketing claims.

---

## Contributing

We welcome high-signal, battle-tested skills from the community:

1. Fork the repository.
2. Create a feature branch (`git checkout -b skill/my-new-skill`).
3. Ensure your skill adheres to the structure:
   ```text
   skills/<skill-name>/
   ├── SKILL.md            # Required: YAML frontmatter + concise runbook
   ├── README.md           # Required: Human documentation
   ├── scripts/            # Optional: Executable helpers (Python/Bash)
   └── references/         # Optional: Deep documentation
   ```
4. Verify all helper scripts run cleanly without unlisted dependencies.
5. Submit a Pull Request.

---

## License

[MIT License](./LICENSE) © 2026 Bulachak. Free to use, adapt, and distribute across commercial and open-source projects.
