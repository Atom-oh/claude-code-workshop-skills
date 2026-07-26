#!/usr/bin/env python3
"""Structural / accessibility self-check for a generated capstone recap page.

Regex-based on purpose: stdlib only, no HTML parser, no dependencies to install mid-workshop.
It catches the mistakes that actually recur in generated single-file pages — it is not a
validator, and it cannot judge whether the content is true.

Usage:
    check_recap_html.py <file.html> [--mobile-breakpoint N] [--allow-abs-paths] [--selftest]

    --mobile-breakpoint N   breakpoint the page is expected to declare (default 768, matching
                            references/design-system.md's two-tier layout).
    --allow-abs-paths       downgrade the absolute-home-path FAIL to a warning, for a page that
                            is deliberately staying on the author's own machine.
    --selftest              run built-in assertions and exit.

Exit codes: 0 = no hard failures, 1 = at least one FAIL (or unreadable file), 2 = usage error.
"""

import os
import re
import sys

TAGS_TO_BALANCE = ("section", "figure", "footer", "style", "table", "head", "body", "main")

ASSET_EXT = (".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif", ".css", ".js")

# Absolute home paths leak the author's directory layout into a page that gets screenshotted
# and shared. Windows form included since a participant may generate on any platform.
ABS_PATH_RE = re.compile(r"(?:/home/[A-Za-z0-9._-]+/|/Users/[A-Za-z0-9._-]+/|[A-Za-z]:\\Users\\)")


def strip_non_visible(html):
    """Drop <style>/<script>/comments so 'visible text' checks don't fire on CSS or JS."""
    html = re.sub(r"<style\b.*?</style>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<script\b.*?</script>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    return html


def visible_text(html):
    """Approximate rendered text: strip non-visible blocks, then all tags."""
    return re.sub(r"<[^>]+>", " ", strip_non_visible(html))


def check(path, breakpoint_px="768", allow_abs_paths=False):
    """Run every check. Returns (oks, warns, fails) as lists of labels."""
    oks, warns, fails = [], [], []

    def need(cond, label, hard=True):
        if cond:
            oks.append(label)
        elif hard:
            fails.append(label)
        else:
            warns.append(label)

    with open(path, encoding="utf-8", errors="replace") as fh:
        html = fh.read()
    base = os.path.dirname(os.path.abspath(path))
    low = html.lower()

    # --- structure -------------------------------------------------------------------
    for tag in TAGS_TO_BALANCE:
        opens = len(re.findall(rf"<{tag}[\s>]", low))
        closes = len(re.findall(rf"</{tag}>", low))
        if opens or closes:
            need(opens == closes, f"tag balance <{tag}> ({opens} open / {closes} close)")

    need("<style" in low, "CSS is inlined (self-contained page)", hard=False)

    # --- responsive ------------------------------------------------------------------
    need('name="viewport"' in low and "width=device-width" in low,
         "viewport meta present with width=device-width")
    need(re.search(rf"@media[^{{]*max-width:\s*{breakpoint_px}", low) is not None,
         f"mobile breakpoint @media max-width:{breakpoint_px} present")

    # --- accessibility ---------------------------------------------------------------
    need(":focus-visible" in low, "visible keyboard focus style (:focus-visible)")
    need("skip-link" in low or re.search(r'href="#(main|content|main-content|overview)"', low) is not None,
         "skip link to main content", hard=False)
    need("prefers-reduced-motion" in low, "prefers-reduced-motion honored")
    if "<animate" in low:
        need(re.search(r"(remove|removeChild|querySelectorAll)\s*\(?[^;]*animate", html) is not None,
             "SMIL <animate> removed in JS under reduced motion (CSS cannot stop SMIL)", hard=False)

    imgs = re.findall(r"<img\b[^>]*>", html, flags=re.I)
    if imgs:
        missing = [t for t in imgs if not re.search(r'alt="[^"]+"', t, flags=re.I)]
        need(not missing, f"every <img> has non-empty alt ({len(imgs) - len(missing)}/{len(imgs)})")
        raster = [t for t in imgs if re.search(r'src="[^"]+\.(png|jpe?g|webp|gif|avif)"', t, flags=re.I)]
        if raster:
            warns.append(
                f"{len(raster)} raster image(s) — eyeball each for baked-in account IDs, ARNs, "
                "tokens or customer data; no text scan can see inside pixels")

    # --- local assets resolve --------------------------------------------------------
    refs = re.findall(r'(?:src|href)="([^"]+)"', html, flags=re.I)
    local = [r for r in refs
             if r.lower().endswith(ASSET_EXT)
             and not r.startswith(("http://", "https://", "//", "data:", "#"))]
    for ref in sorted(set(local)):
        target = os.path.normpath(os.path.join(base, ref.split("?")[0].split("#")[0]))
        need(os.path.isfile(target), f"local asset exists: {ref}")

    # --- leakage ---------------------------------------------------------------------
    leaked = sorted(set(ABS_PATH_RE.findall(visible_text(html))))
    if leaked:
        label = (f"absolute home path in visible text ({', '.join(leaked)}…) — use repo-relative "
                 "paths; this page gets screenshotted and shared")
        if allow_abs_paths:
            warns.append(label + " [--allow-abs-paths]")
        else:
            fails.append(label)
    else:
        oks.append("no absolute home paths in visible text")

    return oks, warns, fails


def report(oks, warns, fails):
    for label in oks:
        print(f"  ok    {label}")
    for label in warns:
        print(f"  WARN  {label}")
    for label in fails:
        print(f"  FAIL  {label}")
    print(f"\n{len(oks)} ok · {len(warns)} warn · {len(fails)} fail")


GOOD_PAGE = """<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:focus-visible{outline:2px solid #b4502c}
@media (max-width:768px){ .wrap{padding:0 18px} }
@media (prefers-reduced-motion: reduce){ *{transition:none} }
/* a CSS comment mentioning /home/someone/ must not trip the leak check */
</style></head><body>
<a class="skip-link" href="#main">Skip</a>
<main id="main"><section><h1>Clawd Jump</h1><p>See docs/superpowers/specs/design.md</p></section></main>
<footer><p>generated 2026-07-26</p></footer>
</body></html>"""


def selftest():
    import tempfile

    def run(html, **kw):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "page.html")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(html)
            for name, body in kw.pop("_assets", {}).items():
                with open(os.path.join(tmp, name), "w", encoding="utf-8") as fh:
                    fh.write(body)
            return check(path, **kw)

    def labels(items):
        return " | ".join(items)

    # A clean page passes with zero failures.
    oks, warns, fails = run(GOOD_PAGE)
    assert not fails, f"clean page should not fail: {labels(fails)}"
    assert any("viewport" in o for o in oks)
    assert any("no absolute home paths" in o for o in oks)

    # Unbalanced tag.
    _, _, fails = run(GOOD_PAGE.replace("</section>", ""))
    assert any("tag balance <section>" in f for f in fails), labels(fails)

    # Missing viewport.
    _, _, fails = run(GOOD_PAGE.replace('<meta name="viewport" content="width=device-width, initial-scale=1">', ""))
    assert any("viewport" in f for f in fails), labels(fails)

    # Wrong breakpoint for the declared expectation.
    _, _, fails = run(GOOD_PAGE, breakpoint_px="640")
    assert any("max-width:640" in f for f in fails), labels(fails)

    # Missing focus style / reduced motion.
    _, _, fails = run(GOOD_PAGE.replace(":focus-visible{outline:2px solid #b4502c}", ""))
    assert any("focus" in f for f in fails), labels(fails)
    _, _, fails = run(GOOD_PAGE.replace("@media (prefers-reduced-motion: reduce){ *{transition:none} }", ""))
    assert any("reduced-motion" in f for f in fails), labels(fails)

    # Leaked absolute home path in VISIBLE text fails; --allow-abs-paths downgrades it.
    leaky = GOOD_PAGE.replace("<p>See docs", "<p>See /home/participant/proj/x.md and docs")
    _, _, fails = run(leaky)
    assert any("absolute home path" in f for f in fails), labels(fails)
    _, warns, fails = run(leaky, allow_abs_paths=True)
    assert not any("absolute home path" in f for f in fails), labels(fails)
    assert any("absolute home path" in w for w in warns), labels(warns)

    # A path inside <style>/<script>/comment is not visible text — must not fail.
    _, _, fails = run(GOOD_PAGE.replace("</style>", "/* /home/me/build.css */\n</style>"))
    assert not any("absolute home path" in f for f in fails), labels(fails)

    # img without alt fails; with alt passes.
    _, _, fails = run(GOOD_PAGE.replace("<h1>", '<img src="shot.png"><h1>'),
                      _assets={"shot.png": "x"})
    assert any("alt" in f for f in fails), labels(fails)
    oks, warns, _ = run(GOOD_PAGE.replace("<h1>", '<img src="shot.png" alt="Gameplay screen"><h1>'),
                        _assets={"shot.png": "x"})
    assert any("alt" in o for o in oks)
    assert any("raster image" in w for w in warns), labels(warns)

    # Missing local asset fails.
    _, _, fails = run(GOOD_PAGE.replace("<h1>", '<img src="missing.png" alt="Gone"><h1>'))
    assert any("local asset exists: missing.png" in f for f in fails), labels(fails)

    print("check_recap_html selftest: all assertions passed")
    return 0


def main(argv):
    args = argv[1:]
    if "--selftest" in args:
        return selftest()

    breakpoint_px = "768"
    if "--mobile-breakpoint" in args:
        i = args.index("--mobile-breakpoint")
        if i + 1 >= len(args):
            print(__doc__)
            return 2
        breakpoint_px = args[i + 1]
        del args[i:i + 2]
    allow_abs = "--allow-abs-paths" in args
    positional = [a for a in args if not a.startswith("--")]
    if len(positional) != 1:
        print(__doc__)
        return 2
    path = positional[0]
    if not os.path.isfile(path):
        print(f"  FAIL  file not found: {path}")
        return 1

    oks, warns, fails = check(path, breakpoint_px=breakpoint_px, allow_abs_paths=allow_abs)
    report(oks, warns, fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
