# Workshop Recap — Claude Code Configuration

Writes up a finished workshop capstone as **one self-contained HTML showcase page**: a detailed
overview of what was built, a demo capture, and an evidenced inventory of which agent capabilities
the project actually used.

The page is built from **content the project already generated** — `CLAUDE.md`/`AGENTS.md`, subagent
definitions, hook wiring, authored skills, MCP config, design specs, CI workflows, IaC — not from
recollection. Every claim cites the real file it came from; anything unevidenced is omitted.

---

## Agents

| Agent | Purpose |
|-------|---------|
| `capstone-recap-agent` | Scans the project, captures a demo, writes and self-checks the showcase page |

## Skills

| Skill | Purpose |
|-------|---------|
| `capstone-recap` | 6-phase workflow: scan → ask gaps → capture → write HTML → self-check → output |

---

## Auto-Invocation Keywords

| Korean | English |
|--------|---------|
| 지금까지 만든 산출물 정리 | summarize what i built |
| 산출물 정리해서 html | workshop recap |
| 워크숍 결과물 정리 | capstone summary |
| 실습 결과 정리 | capstone showcase |
| 캡스톤 정리 | — |
| 캡스톤 결과 페이지 | — |

Not triggered by requests to *do* the work (implementation, review, conversion) or by generic
"make me a landing page" / brochure requests.

---

## Workflow

```
scan_capstone.py (instruction files · subagents · hooks · commands · skills · MCP ·
                  specs · CI · SDK · IaC · git · candidate URLs)
  → AskUserQuestion for gaps only (mission · public URL · reflection)
  → verify URL (curl 200) + capture demo per mission archetype
  → write one self-contained HTML (conditional sections, omit the unevidenced)
  → check_recap_html.py (gate: 0 FAIL)
  → source ledger (claim → file) for user confirmation
```

---

## Never

- Fabricate features, metrics, AWS services, vector stores, recovery narratives, or reflections.
- Put a claim on the page without a source file, a verified URL, or the participant's own words.
- Turn a missing signal into a negative claim — the scanner is best-effort, so "not found" never
  becomes "not used".
- Present a URL as live without an unauthenticated `curl` 200.
- Write into `.claude/`, `.kiro/`, or any settings file. This plugin reads project state and writes
  one HTML file (plus a screenshots dir if it captures any).
- Deploy anything unasked, or overwrite an existing recap page without confirming.
- Emit env var values, secrets, account IDs, or ARNs — and never treat a passing text scan as
  clearing a screenshot; pixels must be checked by eye.
