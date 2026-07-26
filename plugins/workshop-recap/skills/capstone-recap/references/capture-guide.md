# Capture guide — showing what the capstone actually does

A recap page with no visual is a wall of prose about software nobody can see. This guide covers
how to get one honest visual per capstone archetype, and what to do when you can't.

Every workshop capstone deploys a **public URL service**, so a live link is normally the strongest
evidence available — stronger than any screenshot, because a reader can check it themselves. Lead
with the link, support it with a capture.

---

## The fallback ladder

Work down this list and stop at the first rung that produces something real:

1. **Verify the public URL, then screenshot it.**
   ```bash
   curl -s -o /dev/null -w '%{http_code}\n' --max-time 10 "$URL"
   ```
   A `200` means it's genuinely live and unauthenticated — only then present it as live. A `403`
   behind an auth edge, a `404`, or a timeout means the link is not publicly viewable: say so
   plainly rather than linking something a reader will bounce off.
   Then capture with Playwright MCP if those tools are available in the session:
   `browser_navigate` → `browser_resize` to a consistent viewport (1600×900 is a good default, so
   multiple captures look like a set) → `browser_take_screenshot`.
2. **Ask the user for an image file.** Playwright MCP isn't always present (offline sandboxes,
   missing browser deps), and some archetypes have nothing a browser can reach. A screenshot the
   participant already took is just as valid — use `AskUserQuestion` and embed what they provide.
3. **Write an honest text description.** A short factual paragraph of what the thing does beats a
   fabricated visual every time.

**Never** invent a screenshot, use a stock/placeholder image, or describe a screen you haven't
seen. A placeholder is worse than an empty section — it silently misrepresents the work.

---

## Per-mission recipes

### Mission A — Ops monitoring dashboard (S3/CloudFront/Lambda/DynamoDB)
Screenshot the dashboard at its most populated state — an empty dashboard tells the reader nothing.
If it's a **terminal/TUI** dashboard rather than a web one, there's no browser target: a
user-supplied terminal capture is the primary artifact and works exactly the same way in the page.
Prefer a demo/seeded dataset over live production data.

### Mission B — Self-healing autonomous operations center (chaos injection)
The interesting moment is a *recovery*, not steady state. Capture the console/dashboard, and if the
participant ran a chaos experiment, add a short factual note of what was injected and what the
system actually did in response. Only describe what was really observed — a plausible-sounding
recovery narrative that didn't happen is fabrication.

### Mission C — Natural-language ordering system (AI café)
Show one real end-to-end exchange: the utterance, the parsed order, the confirmation. Either a UI
screenshot or a transcript excerpt in a `<pre>` block. Redact anything that looks like a real
customer, phone number, or payment detail.

### Mission D — RAG-based internal librarian (embeddings + vector search)
Show one real query and the answer it returned, ideally with the retrieved source cited — that's
the whole value proposition of a RAG system, and it's the thing a reader wants to judge. Name the
embedding model and vector store **only if the project actually uses them** (check the code/IaC,
don't infer from the mission description). Redact any internal document content that isn't the
participant's to publish.

### Mission E — Browser-based platformer game ("Clawd Jump")
A gameplay screenshot mid-action beats a title screen. An animated GIF is better still if the
participant can produce one. If neither exists, describe the mechanics honestly — no mockup.
Games usually have no architecture worth a section; skip it rather than padding.

### Mission F — Generative-art gallery (Perlin noise / reaction-diffusion)
Screenshot the live URL — this lab states its own principle: *"without a link, you have nothing to
show."* Capture the artwork at a visually developed state (a reaction-diffusion pattern needs time
to evolve; a capture at t=0 is a blank grid). If the gallery has multiple pieces, one capture per
piece in a grid reads far better than a single hero shot.
Note: generative pieces often use SVG/canvas animation — if you embed animated SVG in the recap
page, remove `<animate>` elements in JS under `prefers-reduced-motion` (CSS can't stop SMIL).

### Anything outside these six
Same ladder. Identify what the project's single most convincing visible output is, capture that,
and skip any section the project has no real content for.

---

## Screenshot hygiene

Applies to every capture, whoever produced it:

- **Redact before publishing.** A live console bakes account IDs, ARNs, session tokens in URLs,
  internal hostnames, CIDRs, and customer data into *pixels* — no text-based scan can see them, and
  the checker will not catch them. Prefer a demo/sandbox account with fake data; then eyeball every
  image manually. This is a human gate, and it's the one that matters most before sharing.
- **Optimize.** Target ≤~100KB per image. A recap page shouldn't ship megabytes of raw PNGs.
- **Embed properly.** Save alongside the HTML (e.g. `./shots/`), reference with a relative path,
  add `loading="lazy"`, a descriptive `alt` saying what the screen *shows* (not the filename), and
  a `<figcaption>` naming it. The checker FAILs on a missing or empty `alt`.
- **Keep paths relative.** An absolute `/home/you/...` path in the page is a FAIL — it leaks your
  directory layout into something you're about to screenshot and share.
