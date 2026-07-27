---
name: capstone-recap
description: "Turn a finished workshop capstone into one polished, self-contained HTML showcase page — detailed overview, live demo capture, and an evidenced inventory of which agent capabilities the project used. Built from the project's own generated content (CLAUDE.md/AGENTS.md, subagent definitions, hooks and settings, authored skills, MCP servers, design specs, CI workflows, IaC), never from recollection: every claim cites the real file it came from and anything unevidenced is omitted. Use when a participant wants their work written up — '지금까지 만든 산출물을 정리해서 html로 만들어줘', '워크숍 결과물 정리해줘', '캡스톤 정리 페이지', 'workshop recap', 'capstone summary page', 'summarize what I built as an HTML page'. NOT for doing the capstone work itself (that's the project's own tooling), and NOT a product brochure or marketing landing page."
triggers:
  # Retrospective / write-up phrasings only. Deliberately excluded:
  #  - doing-the-work phrasings ("kiro로 구현", "co-agent로 리뷰", "키로 변환") — those plugins
  #    own them, and matching here would load this skill for an unrelated request.
  #  - bare "html 만들어줘" with no retrospective object — too broad, would hijack any
  #    web-page request.
  #  - product marketing pages ("브로셔", "랜딩 페이지") — not this skill's job.
  - "지금까지 만든 산출물 정리"
  - "산출물 정리해서 html"
  - "워크숍 결과물 정리"
  - "실습 결과 정리"
  - "캡스톤 정리"
  - "캡스톤 결과 페이지"
  - "workshop recap"
  - "capstone summary"
  - "capstone showcase"
  - "summarize what i built"
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
---

# capstone-recap — write up a finished capstone as one HTML page

Build a **single self-contained HTML page** (one `.html` with CSS inlined, plus any screenshots
beside it) that shows what a workshop participant built and which agent capabilities they used
building it. No build step, no framework, no server.

> Read **`references/design-system.md`** before writing any CSS, and **`references/capture-guide.md`**
> before capturing the demo. The owning agent is `capstone-recap-agent`.
> `{skill-dir}` below = `${CLAUDE_PLUGIN_ROOT}/skills/capstone-recap`.

**The page is written from generated content, not from an interview.** The project's own
`CLAUDE.md`, subagent files, hook wiring, specs, workflows, and IaC are the facts. Ask the
participant only for what those files genuinely cannot tell you. **A claim with no source does not
go on the page.**

## When this applies

- **Use this skill** when the capstone is finished and the participant wants it written up:
  "지금까지 만든 산출물을 정리해서 html로 만들어줘", "캡스톤 정리 페이지 만들어줘",
  "workshop recap page".
- **Don't use it** to *do* the capstone, to review code, or to produce a product brochure /
  marketing landing page. It summarizes work that already exists.

The workshop it serves ends in one of six capstone missions — ops dashboard, self-healing ops
center, NL ordering system, RAG librarian, browser platformer, generative-art gallery — each
deploying a public URL. The page must fit any of them, so **every section except hero/overview/
footer is conditional**: include it when there's evidence, omit it otherwise. Never pad with
placeholders.

---

## Phase 1 — Scan the project

Start here, before asking anything:

```bash
python3 "{skill-dir}/scripts/scan_capstone.py" <project-dir> --json
```

It inventories, with a real path attached to each item: instruction files (`CLAUDE.md`/`AGENTS.md`),
subagents, slash commands, authored skills, hook wirings, settings surface (permission counts and
env var **names** only), MCP servers, packaged plugins, specs/plans, CI workflows, Agent SDK usage,
IaC, project metadata, candidate public URLs, and git facts.

Then read the highest-signal files it found — the root instruction file and README are where the
overview copy comes from. Quote and condense them; don't reinvent the project's own description.
Instruction files are returned project-owned-first; one marked `describes_plugin` documents a
**bundled plugin, not the capstone** — never source the overview from it.

**Absence is not a finding.** If the scan reports no hooks, the page says nothing about hooks. It
must never say "no hooks were used" — the participant may have done work the scanner can't see.

### Ask only for the gaps

One `AskUserQuestion` round, pre-filled with what was found, covering only:

- **Mission / project identity** — if not derivable from the instruction file or README.
- **The public URL** — if no candidate was found. Every mission deploys one, so ask for it rather
  than asking *whether* it exists.
- **Reflection** — the participant's own "what I learned". If they skip it, the section is omitted,
  not invented.

If the scan found essentially nothing (no instruction file, no capabilities, no git history), say
so plainly and ask what was built before writing any HTML. Don't generate a page about a project
you can't see.

---

## Phase 2 — Capture the demo

Follow **`references/capture-guide.md`** — it has a recipe per mission and the fallback ladder.
Summary: verify the URL, then screenshot; if you can't, ask for an image; if there's none, write an
honest description. Never a placeholder.

```bash
curl -s -o /dev/null -w '%{http_code}\n' --max-time 10 "$URL"
```

Only a `200` justifies presenting the link as live. Anything else — say what the status was.

---

## Phase 3 — Commit to a design direction

Read `references/design-system.md` and execute one direction precisely. It ships a concrete token
set, typography pairing, the two-tier 768 breakpoint, the accessibility checklist, and the CSS
gotchas that recur in generated pages. A capstone with its own visual identity (a game, an art
gallery) may use that project's palette instead — deliberate reuse is better than the default, as
long as contrast still passes.

---

## Phase 4 — Write the HTML

One file, CSS inlined. Section spine — **conditional sections are omitted when unevidenced**:

| Section | Source | Required? |
|---|---|---|
| `nav` | — | optional (skip on a short page) |
| `hero` | project name · mission · one-liner · live URL as CTA | yes |
| `overview` | instruction file / README, condensed and cited | yes |
| `demo` | Phase 2 capture | when a capture exists |
| `architecture` | IaC + instruction file | when the project has one |
| `capabilities` | the scan: subagents, hooks, commands, skills, MCP, CI, SDK — **each row names its source file** | when any were found |
| `process` | specs/plans found by the scan | when they exist |
| `stats` | git counts, capability counts — real numbers only | omit tiles with no number |
| `reflection` | the participant's own words | when they provided them |
| `footer` | generated date, repo | yes |

`capabilities` is the section a product brochure has no analogue for, and it's the workshop's
actual payload — treat it as a first-class part of the page, not an appendix. Render each entry in
mono with its path, e.g. `level-designer` → `.claude/agents/level-designer.md`.

---

## Phase 5 — Self-check

```bash
python3 "{skill-dir}/scripts/check_recap_html.py" <page.html>
```

Gate: **0 FAIL**. Each WARN is either fixed or reported to the participant with a reason. Add
`--mobile-breakpoint N` if the page deliberately uses a breakpoint other than 768;
`--allow-abs-paths` only for a page that is knowingly never leaving the author's machine.

There is no content-scoring reviewer in this marketplace, so the second half of the gate is
factual, not numeric: print a **source ledger** — one line per claim, `claim → source` (real path,
verified URL, or `self-reported`) — and get the participant's confirmation. **A claim they dispute
is deleted, not softened.**

---

## Phase 6 — Output

Write `./capstone-recap.html` (or a name matching the project) in the project dir. Confirm before
overwriting an existing recap. Deploying the recap page itself is opt-in only: if asked, publish
via GitHub Pages and verify with the same unauthenticated `curl` 200 check, after re-reading every
embedded excerpt for anything that shouldn't be public.

---

## Never

- Fabricate features, metrics, services, vector stores, recovery narratives, or reflections.
- Put a claim on the page without a source file, verified URL, or the participant's own words.
- Turn a missing signal into a negative claim ("no hooks were used").
- Present a URL as live without an unauthenticated 200.
- Write into `.claude/`, `.kiro/`, or any settings file — this skill reads project state and writes
  one HTML file (plus a screenshots dir).
- Deploy anything unasked, or overwrite an existing recap without confirming.
- Emit env var **values**, secrets, account IDs, or ARNs; and never assume a text scan cleared a
  screenshot — pixels have to be checked by eye.

---

## References

- `references/design-system.md` — tokens, typography, responsive tiers, accessibility, CSS gotchas.
- `references/capture-guide.md` — per-mission demo capture recipes, fallback ladder, screenshot hygiene.
- `scripts/scan_capstone.py` — project inventory → JSON (`--selftest` for its own assertions).
- `scripts/check_recap_html.py` — structural/accessibility gate (`--selftest` likewise).
