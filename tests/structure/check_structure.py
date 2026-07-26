#!/usr/bin/env python3
"""Structural checks for this marketplace's plugins — the audit this file codifies was
run ad-hoc once; this makes it repeatable. Emits one `PASS|FAIL<TAB>description<TAB>detail`
line per check to stdout; `tests/structure/test-plugin-structure.sh` sources these into the
tests/run-all.sh counters. Not a general-purpose linter — checks only what this repo's own
audit found worth guarding (manifest validity, declared-file existence, version sync,
executable bits, ${CLAUDE_PLUGIN_ROOT} path resolution, and the co-agent<->kiro verbatim
script pairs staying byte-identical).

Usage: check_structure.py <repo_root>
"""
import json
import os
import re
import sys
import glob


def emit(ok, desc, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}\t{desc}\t{detail}")


def load_json(path):
    try:
        return json.load(open(path, encoding="utf-8")), None
    except Exception as e:
        return None, str(e)


def frontmatter(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    fields = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^([a-zA-Z_-]+):\s*(.*)$", line)
        if m:
            fields[m.group(1)] = m.group(2).strip()
    return fields


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(root)

    # --- marketplace.json ---
    mk_path = ".claude-plugin/marketplace.json"
    mk, err = load_json(mk_path)
    emit(mk is not None, "marketplace.json is valid JSON", err or "")
    if mk is None:
        return
    plugins = mk.get("plugins", [])
    emit(len(plugins) > 0, "marketplace.json declares at least one plugin")

    versions = {}  # path -> version, for the cross-manifest version-sync check
    for p in plugins:
        name = p.get("name")
        source = (p.get("source") or p.get("path") or "").lstrip("./")
        emit(bool(source) and os.path.isdir(source),
             f"marketplace source dir exists: {name}", source)
        versions[mk_path + f" ({name})"] = p.get("version")

    # --- per-plugin manifests ---
    plugin_dirs = sorted(glob.glob("plugins/*/"))
    for pdir in plugin_dirs:
        pname = pdir.rstrip("/").split("/")[-1]
        for manifest in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
            mpath = os.path.join(pdir, manifest)
            if not os.path.isfile(mpath):
                emit(False, f"{pname}: {manifest} exists", mpath)
                continue
            d, err = load_json(mpath)
            emit(d is not None, f"{pname}: {manifest} is valid JSON", err or "")
            if d is None:
                continue
            versions[mpath] = d.get("version")
            if manifest == ".claude-plugin/plugin.json":
                for key in ("agents", "skills", "commands"):
                    v = d.get(key)
                    if isinstance(v, str):
                        v = [v]
                    for item in (v or []):
                        ipath = os.path.join(pdir, item.lstrip("./"))
                        emit(os.path.exists(ipath),
                             f"{pname}: declared {key} file exists", item)

    # --- version sync across every manifest + marketplace entry ---
    distinct = set(v for v in versions.values() if v)
    emit(len(distinct) <= 1, "all manifest versions match",
         "" if len(distinct) <= 1 else json.dumps(versions))

    # --- skill name == directory name, agent name == file name ---
    for skill_md in sorted(glob.glob("plugins/*/skills/*/SKILL.md")):
        fm = frontmatter(skill_md)
        dirname = os.path.basename(os.path.dirname(skill_md))
        emit(bool(fm and fm.get("name") == dirname),
             f"skill name matches directory: {skill_md}",
             f"name={fm.get('name') if fm else None} dir={dirname}")

    for agent_md in sorted(glob.glob("plugins/*/agents/*.md")):
        fm = frontmatter(agent_md)
        filename = os.path.basename(agent_md)[:-3]
        emit(bool(fm and fm.get("name") == filename),
             f"agent name matches filename: {agent_md}",
             f"name={fm.get('name') if fm else None} file={filename}")

    # --- executable bits on every shipped script ---
    for script in sorted(glob.glob("plugins/**/*.py", recursive=True) +
                          glob.glob("plugins/**/*.sh", recursive=True)):
        emit(os.access(script, os.X_OK), f"script is executable: {script}")

    # --- ${CLAUDE_PLUGIN_ROOT} references resolve to real files, within their own plugin ---
    ref_re = re.compile(r'\$\{CLAUDE_PLUGIN_ROOT\}/([^\s"\'`)]+)')
    for pdir in plugin_dirs:
        for doc in glob.glob(os.path.join(pdir, "**", "*.md"), recursive=True) + \
                   glob.glob(os.path.join(pdir, "**", "*.json"), recursive=True):
            try:
                text = open(doc, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for m in ref_re.finditer(text):
                rel = m.group(1)
                target = os.path.join(pdir, rel)
                emit(os.path.exists(target),
                     f"${{CLAUDE_PLUGIN_ROOT}} ref resolves: {doc}", rel)

    # --- co-agent <-> kiro verbatim-copied scripts stay byte-identical ---
    pairs = [
        ("plugins/co-agent/skills/co-agent/scripts/parse_plan.py",
         "plugins/kiro/skills/kiro-delegate/scripts/parse_plan.py"),
        ("plugins/co-agent/skills/co-agent/scripts/scope_guard.py",
         "plugins/kiro/skills/kiro-delegate/scripts/scope_guard.py"),
        ("plugins/co-agent/skills/co-agent/scripts/worktree.py",
         "plugins/kiro/skills/kiro-delegate/scripts/worktree.py"),
    ]
    for a, b in pairs:
        if not (os.path.isfile(a) and os.path.isfile(b)):
            emit(False, f"verbatim pair present: {a} <-> {b}", "one or both missing")
            continue
        ca, cb = open(a, "rb").read(), open(b, "rb").read()
        emit(ca == cb, f"verbatim pair byte-identical: {os.path.basename(a)}",
             "" if ca == cb else "kiro's copy has drifted from co-agent's — sync it or "
                                  "document the intentional divergence")


if __name__ == "__main__":
    main()
