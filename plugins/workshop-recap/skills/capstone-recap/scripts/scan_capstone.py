#!/usr/bin/env python3
"""Inventory a capstone project's generated content, so a recap page can cite it.

Every item reported carries the real path it came from — the recap page's honesty rule is that a
claim without a source file does not get rendered, and this script is what supplies the sources.

Usage:
    scan_capstone.py [PROJECT_DIR] [--json] [--selftest]

    PROJECT_DIR  defaults to the current directory.
    --json       machine-readable output (default is a human-readable summary).
    --selftest   run built-in assertions against a synthetic project tree and exit.

Deliberately conservative: it reports what it finds and stays silent about what it doesn't.
Absence of a signal means "not evidenced", never "not used" — the caller must not turn a missing
key into a claim that the participant skipped something.
"""

import glob
import json
import os
import re
import subprocess
import sys

# Agent-instruction filenames, in the order we prefer them as the overview source.
INSTRUCTION_FILES = ("CLAUDE.md", "AGENTS.md", "GEMINI.md")

IAC_MARKERS = {
    "cdk.json": "AWS CDK",
    "template.yaml": "AWS SAM / CloudFormation",
    "template.yml": "AWS SAM / CloudFormation",
    "serverless.yml": "Serverless Framework",
    "serverless.yaml": "Serverless Framework",
    "samconfig.toml": "AWS SAM",
}

SDK_PATTERNS = (
    r"@anthropic-ai/claude-agent-sdk",
    r"@anthropic-ai/claude-code",
    r"claude_agent_sdk",
    r"claude-agent-sdk",
    r"anthropic",
)

# Directories never worth walking — vendored deps and build output dwarf real content.
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
    ".next", ".docusaurus", "cdk.out", ".pytest_cache", ".mypy_cache", ".terraform",
}

URL_RE = re.compile(
    r"https?://[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]*"
    r"(?:cloudfront\.net|amazonaws\.com|github\.io|vercel\.app|netlify\.app|pages\.dev|workers\.dev)"
    r"[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]*"
)


def frontmatter(path):
    """Parse a leading YAML frontmatter block into a flat dict of scalars.

    Intentionally naive (same shape as the repo's own structure checker): top-level `key: value`
    lines only. Enough to read a subagent's name/description/tools/model.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError):
        return {}
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    out = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return out


def rel(root, path):
    return os.path.relpath(path, root).replace(os.sep, "/")


def find_files(root, pattern, limit=200):
    """Glob relative to root, skipping vendored/build dirs, returning repo-relative paths."""
    hits = []
    for path in glob.glob(os.path.join(root, pattern), recursive=True):
        parts = set(os.path.relpath(path, root).split(os.sep))
        if parts & SKIP_DIRS:
            continue
        if os.path.isfile(path):
            hits.append(rel(root, path))
        if len(hits) >= limit:
            break
    return sorted(hits)


def read_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError, UnicodeDecodeError):
        return None


def scan_instructions(root):
    """Agent instruction files — the richest source for the project overview.

    A CLAUDE.md bundled *inside a plugin* documents that plugin, not the capstone, so it must not
    be cited as the project's own description. Such files are still reported, but flagged
    `describes_plugin` so the caller can prefer the real ones; `root_level` marks the top-level
    file, which is the best overview source when it exists.
    """
    found = []
    for name in INSTRUCTION_FILES:
        for path in find_files(root, f"**/{name}"):
            parts = path.split("/")
            # Inside a plugin if any ancestor dir carries a plugin manifest.
            describes_plugin = False
            for i in range(len(parts) - 1):
                ancestor = "/".join(parts[:i + 1])
                if os.path.isdir(os.path.join(root, ancestor, ".claude-plugin")):
                    describes_plugin = True
                    break
            found.append({
                "path": path,
                "lines": sum(1 for _ in open(os.path.join(root, path), encoding="utf-8", errors="replace")),
                "root_level": len(parts) == 1,
                "describes_plugin": describes_plugin,
            })
    # Root-level and project-owned files first — the caller reads from the top.
    found.sort(key=lambda f: (f["describes_plugin"], not f["root_level"], f["path"]))
    return found


def scan_subagents(root):
    """Subagent definitions (workshop Ch 2) — .claude/agents/ and plugin agents/."""
    out = []
    for path in find_files(root, ".claude/agents/*.md") + find_files(root, "**/agents/*.md"):
        if any(a["path"] == path for a in out):
            continue
        fm = frontmatter(os.path.join(root, path))
        if not fm.get("name"):
            continue
        out.append({
            "path": path,
            "name": fm.get("name"),
            "description": fm.get("description", "")[:300],
            "tools": fm.get("tools", ""),
            "model": fm.get("model", ""),
        })
    return out


def scan_commands(root):
    """Slash commands: .claude/commands/, or a plugin's commands/ dir.

    A bare "**/commands/*.md" glob is too loose — a docs site page *about* commands
    (doc-sites/docs/<plugin>/commands/commands.md) would be reported as a command the project
    defines, putting a fabricated row on the recap page. Require either the .claude/commands
    location or a commands/ dir that sits beside a .claude-plugin/ manifest.
    """
    out = []
    for path in find_files(root, ".claude/commands/**/*.md") + find_files(root, "**/commands/*.md"):
        if any(c["path"] == path for c in out):
            continue
        parent = os.path.dirname(path)
        in_claude_dir = parent.endswith(".claude/commands") or "/.claude/commands/" in f"/{path}"
        plugin_dir = os.path.dirname(parent)
        is_plugin_command = os.path.isdir(os.path.join(root, plugin_dir, ".claude-plugin"))
        if not (in_claude_dir or is_plugin_command):
            continue
        fm = frontmatter(os.path.join(root, path))
        name = os.path.basename(path)[:-3]
        out.append({
            "path": path,
            "name": f"/{name}",
            "description": fm.get("description", "")[:300],
        })
    return out


def scan_skills(root):
    out = []
    for path in find_files(root, "**/skills/*/SKILL.md"):
        fm = frontmatter(os.path.join(root, path))
        out.append({
            "path": path,
            "name": fm.get("name") or os.path.basename(os.path.dirname(path)),
            "description": fm.get("description", "")[:300],
        })
    return out


def scan_hooks(root):
    """Hook wiring from settings files (workshop Ch 3/4). Reports event names + matchers."""
    out = []
    for path in find_files(root, ".claude/settings*.json") + find_files(root, "**/.claude-plugin/plugin.json"):
        data = read_json(os.path.join(root, path))
        if not isinstance(data, dict):
            continue
        hooks = data.get("hooks")
        if not isinstance(hooks, dict):
            continue
        for event, entries in hooks.items():
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                inner = entry.get("hooks") or []
                out.append({
                    "path": path,
                    "event": event,
                    "matcher": entry.get("matcher", ""),
                    "count": len(inner) if isinstance(inner, list) else 0,
                })
    return out


def scan_settings(root):
    """Permissions / env surface — evidence of config-layer work, without dumping secrets."""
    out = []
    for path in find_files(root, ".claude/settings*.json"):
        data = read_json(os.path.join(root, path))
        if not isinstance(data, dict):
            continue
        perms = data.get("permissions") or {}
        entry = {"path": path, "keys": sorted(k for k in data if k != "hooks")}
        if isinstance(perms, dict):
            entry["allow_count"] = len(perms.get("allow") or [])
            entry["deny_count"] = len(perms.get("deny") or [])
        # Env var NAMES only — values may hold credentials and must never reach the page.
        env = data.get("env")
        if isinstance(env, dict):
            entry["env_names"] = sorted(env.keys())
        out.append(entry)
    return out


def scan_mcp(root):
    # "**/" already covers the project root, so one pattern is enough — globbing ".mcp.json"
    # as well would double-count a root-level file and inflate the server tally.
    out = []
    for path in find_files(root, "**/.mcp.json"):
        data = read_json(os.path.join(root, path))
        if not isinstance(data, dict):
            continue
        servers = data.get("mcpServers")
        if isinstance(servers, dict) and servers:
            out.append({"path": path, "servers": sorted(servers.keys())})
    return out


def scan_plugins(root):
    out = []
    for path in find_files(root, "**/.claude-plugin/plugin.json"):
        data = read_json(os.path.join(root, path))
        if not isinstance(data, dict) or not data.get("name"):
            continue
        out.append({
            "path": path,
            "name": data.get("name"),
            "version": data.get("version", ""),
            "agents": len(data.get("agents") or []),
            "skills": len(data.get("skills") or []),
            "commands": len(data.get("commands") or []),
        })
    return out


def scan_specs(root):
    """brainstorm -> plan -> execute artifacts."""
    patterns = (
        "docs/superpowers/specs/*.md",
        "docs/superpowers/plans/*.md",
        "docs/specs/*.md",
        "docs/plans/*.md",
        "specs/*.md",
    )
    out = []
    for pattern in patterns:
        for path in find_files(root, pattern):
            if any(s["path"] == path for s in out):
                continue
            out.append({
                "path": path,
                "title": first_heading(os.path.join(root, path)),
            })
    return out


def first_heading(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if line.startswith("# "):
                    return line[2:].strip()
    except OSError:
        pass
    return ""


def scan_workflows(root):
    out = []
    for path in find_files(root, ".github/workflows/*.y*ml"):
        name = ""
        try:
            with open(os.path.join(root, path), encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    m = re.match(r"^name:\s*(.+)$", line)
                    if m:
                        name = m.group(1).strip().strip('"').strip("'")
                        break
        except OSError:
            pass
        out.append({"path": path, "name": name or os.path.basename(path)})
    return out


def scan_sdk(root):
    """Agent SDK usage (workshop Ch 6) — dependency manifests and direct imports."""
    hits = []
    manifests = (find_files(root, "**/package.json") + find_files(root, "**/requirements.txt")
                 + find_files(root, "**/pyproject.toml"))
    for path in manifests:
        if "/node_modules/" in path:
            continue
        try:
            text = open(os.path.join(root, path), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for pattern in SDK_PATTERNS:
            if re.search(pattern, text):
                hits.append({"path": path, "match": pattern})
                break
    return hits


def scan_iac(root):
    out = []
    for marker, label in IAC_MARKERS.items():
        for path in find_files(root, f"**/{marker}"):
            out.append({"path": path, "kind": label})
    # Report the Terraform root(s), not every module file — but cite a real directory rather than
    # one arbitrary .tf, since a multi-root project would otherwise be represented by whichever
    # file happened to sort first.
    tf_dirs = sorted({os.path.dirname(p) or "." for p in find_files(root, "**/*.tf", limit=200)})
    for d in tf_dirs[:5]:
        out.append({"path": d, "kind": "Terraform"})
    return out


def scan_project_meta(root):
    """Project name / description / scripts, from package.json then README."""
    meta = {}
    pkg_path = os.path.join(root, "package.json")
    pkg = read_json(pkg_path)
    if isinstance(pkg, dict):
        meta["package_json"] = {
            "path": "package.json",
            "name": pkg.get("name", ""),
            "description": pkg.get("description", ""),
            "scripts": sorted((pkg.get("scripts") or {}).keys()),
        }
    for name in ("README.md", "README.rst", "readme.md"):
        path = os.path.join(root, name)
        if os.path.isfile(path):
            meta["readme"] = {"path": name, "title": first_heading(path)}
            break
    return meta


def scan_public_urls(root):
    """Candidate public URLs from README / IaC outputs / workflows. Unverified by design."""
    candidates = {}
    sources = ["README.md", "readme.md"]
    sources += find_files(root, ".github/workflows/*.y*ml")
    sources += find_files(root, "cdk-outputs*.json") + find_files(root, "outputs*.json")
    for path in sources:
        full = os.path.join(root, path)
        if not os.path.isfile(full):
            continue
        try:
            text = open(full, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for url in URL_RE.findall(text):
            url = url.rstrip(").,;'\"")
            candidates.setdefault(url, path)
    return [{"url": u, "found_in": p} for u, p in sorted(candidates.items())]


def scan_git(root):
    """Commit/file counts. Numbers here are real; absent keys mean 'not a git repo'."""
    def run(args):
        try:
            res = subprocess.run(args, cwd=root, capture_output=True, text=True, timeout=15)
        except (OSError, subprocess.SubprocessError):
            return None
        return res.stdout.strip() if res.returncode == 0 else None

    if run(["git", "rev-parse", "--git-dir"]) is None:
        return {}
    out = {}
    count = run(["git", "rev-list", "--count", "HEAD"])
    if count and count.isdigit():
        out["commits"] = int(count)
    log = run(["git", "log", "--oneline", "-20", "--no-decorate"])
    if log:
        out["recent_commits"] = log.splitlines()
    tracked = run(["git", "ls-files"])
    if tracked:
        out["tracked_files"] = len(tracked.splitlines())
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if branch:
        out["branch"] = branch
    # `git log --reverse -1` still yields the NEWEST commit (-1 is applied before --reverse),
    # so take the last line of the full oldest-first list instead.
    stamps = run(["git", "log", "--reverse", "--format=%aI"])
    if stamps:
        lines = stamps.splitlines()
        out["first_commit_at"] = lines[0]
        out["last_commit_at"] = lines[-1]
    return out


def scan(root):
    root = os.path.abspath(root)
    inv = {
        "project_dir": root,
        "instructions": scan_instructions(root),
        "subagents": scan_subagents(root),
        "commands": scan_commands(root),
        "skills": scan_skills(root),
        "hooks": scan_hooks(root),
        "settings": scan_settings(root),
        "mcp": scan_mcp(root),
        "plugins": scan_plugins(root),
        "specs": scan_specs(root),
        "workflows": scan_workflows(root),
        "agent_sdk": scan_sdk(root),
        "iac": scan_iac(root),
        "meta": scan_project_meta(root),
        "public_url_candidates": scan_public_urls(root),
        "git": scan_git(root),
    }
    inv["capability_summary"] = {
        "subagents": len(inv["subagents"]),
        "slash_commands": len(inv["commands"]),
        "skills": len(inv["skills"]),
        "hook_wirings": len(inv["hooks"]),
        "mcp_servers": sum(len(m["servers"]) for m in inv["mcp"]),
        "plugins_packaged": len(inv["plugins"]),
        "ci_workflows": len(inv["workflows"]),
        "specs": len(inv["specs"]),
        "uses_agent_sdk": bool(inv["agent_sdk"]),
    }
    return inv


def render_summary(inv):
    lines = [f"Capstone inventory — {inv['project_dir']}", ""]
    cap = inv["capability_summary"]
    lines.append("Capabilities evidenced:")
    for key in ("subagents", "slash_commands", "skills", "hook_wirings", "mcp_servers",
                "plugins_packaged", "ci_workflows", "specs"):
        if cap[key]:
            lines.append(f"  {key:18} {cap[key]}")
    if cap["uses_agent_sdk"]:
        lines.append(f"  {'agent_sdk':18} yes")
    if not any(cap[k] for k in cap if k != "uses_agent_sdk") and not cap["uses_agent_sdk"]:
        lines.append("  (none found — the page must not claim any)")
    lines.append("")

    def block(title, items, fmt):
        if not items:
            return
        lines.append(f"{title}:")
        for item in items[:25]:
            lines.append("  " + fmt(item))
        if len(items) > 25:
            lines.append(f"  ... {len(items) - 25} more")
        lines.append("")

    block("Instruction files", inv["instructions"],
          lambda i: f"{i['path']} ({i['lines']} lines)"
                    + ("  [documents a bundled plugin — not the capstone]" if i["describes_plugin"] else ""))
    block("Subagents", inv["subagents"], lambda i: f"{i['name']:24} {i['path']}")
    block("Slash commands", inv["commands"], lambda i: f"{i['name']:24} {i['path']}")
    block("Skills", inv["skills"], lambda i: f"{i['name']:24} {i['path']}")
    block("Hooks", inv["hooks"],
          lambda i: f"{i['event']:16} matcher={i['matcher'] or '-':12} x{i['count']}  {i['path']}")
    block("MCP servers", inv["mcp"], lambda i: f"{', '.join(i['servers'])}  ({i['path']})")
    block("Plugins packaged", inv["plugins"],
          lambda i: f"{i['name']:24} agents={i['agents']} skills={i['skills']} cmds={i['commands']}")
    block("Specs / plans", inv["specs"], lambda i: f"{i['path']}  {i['title']}")
    block("CI workflows", inv["workflows"], lambda i: f"{i['name']:28} {i['path']}")
    block("Agent SDK", inv["agent_sdk"], lambda i: f"{i['match']}  ({i['path']})")
    block("Infrastructure as code", inv["iac"], lambda i: f"{i['kind']:28} {i['path']}")
    block("Public URL candidates (UNVERIFIED — curl before presenting)",
          inv["public_url_candidates"], lambda i: f"{i['url']}  <- {i['found_in']}")

    git = inv["git"]
    if git:
        lines.append("Git:")
        for key in ("branch", "commits", "tracked_files", "first_commit_at", "last_commit_at"):
            if key in git:
                lines.append(f"  {key:18} {git[key]}")
        lines.append("")
    return "\n".join(lines)


def selftest():
    """Assert the scanner finds what it should in a synthetic tree, and invents nothing."""
    import tempfile

    def write(path, text):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    with tempfile.TemporaryDirectory() as tmp:
        write(f"{tmp}/CLAUDE.md", "# Clawd Jump\n\nA browser platformer.\n")
        write(f"{tmp}/README.md", "# Clawd Jump\n\nLive: https://d123.cloudfront.net/index.html\n")
        write(f"{tmp}/.claude/agents/level-designer.md",
              '---\nname: level-designer\ndescription: "Designs levels."\ntools: Read, Write\nmodel: sonnet\n---\n\nBody.\n')
        write(f"{tmp}/.claude/commands/ship.md", '---\ndescription: "Ship it."\n---\n\nDo it.\n')
        write(f"{tmp}/.claude/settings.json", json.dumps({
            "permissions": {"allow": ["Bash(npm:*)"], "deny": []},
            "env": {"SECRET_TOKEN": "sk-should-not-leak"},
            "hooks": {"PostToolUse": [{"matcher": "Edit", "hooks": [{"type": "command", "command": "true"}]}]},
        }))
        write(f"{tmp}/.mcp.json", json.dumps({"mcpServers": {"playwright": {"command": "npx"}}}))
        write(f"{tmp}/docs/superpowers/specs/2026-07-26-clawd-jump-design.md", "# Clawd Jump design\n")
        write(f"{tmp}/.github/workflows/deploy.yml", "name: Deploy\non: push\n")
        write(f"{tmp}/package.json", json.dumps({
            "name": "clawd-jump", "description": "platformer",
            "scripts": {"build": "vite build"},
            "dependencies": {"@anthropic-ai/claude-agent-sdk": "^1.0.0"},
        }))
        write(f"{tmp}/cdk.json", "{}")
        # Noise that must be ignored, not reported.
        write(f"{tmp}/node_modules/junk/CLAUDE.md", "# vendored, must be skipped\n")
        write(f"{tmp}/node_modules/junk/package.json", json.dumps({"name": "junk"}))
        # A docs page ABOUT commands is not a command the project defines.
        write(f"{tmp}/doc-sites/docs/guide/commands/commands.md", "# Commands reference\n")

        inv = scan(tmp)
        cap = inv["capability_summary"]

        assert [i["path"] for i in inv["instructions"]] == ["CLAUDE.md"], inv["instructions"]
        assert inv["instructions"][0]["root_level"] is True
        assert inv["instructions"][0]["describes_plugin"] is False
        assert cap["subagents"] == 1, inv["subagents"]
        assert inv["subagents"][0]["name"] == "level-designer"
        assert inv["subagents"][0]["model"] == "sonnet"
        # Exactly one: /ship. The doc-sites commands page must NOT be counted.
        assert cap["slash_commands"] == 1, inv["commands"]
        assert inv["commands"][0]["name"] == "/ship", inv["commands"]
        assert not any("doc-sites" in c["path"] for c in inv["commands"]), inv["commands"]
        assert cap["hook_wirings"] == 1 and inv["hooks"][0]["event"] == "PostToolUse"
        assert inv["hooks"][0]["matcher"] == "Edit"
        assert cap["mcp_servers"] == 1 and inv["mcp"][0]["servers"] == ["playwright"]
        assert cap["specs"] == 1, inv["specs"]
        assert cap["ci_workflows"] == 1 and inv["workflows"][0]["name"] == "Deploy"
        assert cap["uses_agent_sdk"] is True, inv["agent_sdk"]
        assert any(i["kind"] == "AWS CDK" for i in inv["iac"]), inv["iac"]
        assert inv["meta"]["package_json"]["name"] == "clawd-jump"
        urls = [c["url"] for c in inv["public_url_candidates"]]
        assert "https://d123.cloudfront.net/index.html" in urls, urls

        # Env var VALUES must never be reported — only names.
        blob = json.dumps(inv)
        assert "sk-should-not-leak" not in blob, "settings env values leaked into the inventory"
        assert inv["settings"][0]["env_names"] == ["SECRET_TOKEN"]
        # Vendored dirs must be skipped entirely.
        assert "node_modules" not in blob, "node_modules content leaked into the inventory"

    # A CLAUDE.md bundled inside a plugin documents the plugin, not the capstone — it must be
    # flagged and must never outrank the project's own root instruction file.
    with tempfile.TemporaryDirectory() as tmp:
        write(f"{tmp}/CLAUDE.md", "# The capstone itself\n")
        write(f"{tmp}/plugins/mytool/.claude-plugin/plugin.json", json.dumps({"name": "mytool"}))
        write(f"{tmp}/plugins/mytool/CLAUDE.md", "# mytool plugin docs\n")
        instructions = scan(tmp)["instructions"]
        by_path = {i["path"]: i for i in instructions}
        assert by_path["CLAUDE.md"]["describes_plugin"] is False, instructions
        assert by_path["plugins/mytool/CLAUDE.md"]["describes_plugin"] is True, instructions
        assert instructions[0]["path"] == "CLAUDE.md", \
            f"project's own instruction file must sort first: {instructions}"

    # Multiple Terraform roots are reported as directories, not one arbitrary .tf file.
    with tempfile.TemporaryDirectory() as tmp:
        write(f"{tmp}/infra/main.tf", "resource {}\n")
        write(f"{tmp}/infra/vars.tf", "variable {}\n")
        write(f"{tmp}/modules/net/main.tf", "resource {}\n")
        tf = [i["path"] for i in scan(tmp)["iac"] if i["kind"] == "Terraform"]
        assert tf == ["infra", "modules/net"], tf

    with tempfile.TemporaryDirectory() as empty:
        inv = scan(empty)
        cap = inv["capability_summary"]
        assert cap["subagents"] == 0 and cap["hook_wirings"] == 0
        assert cap["uses_agent_sdk"] is False
        assert inv["public_url_candidates"] == []
        assert inv["instructions"] == []
        assert inv["git"] == {}, "a non-git dir must report no git facts"

    # first_commit_at must be the OLDEST commit, not the newest (`git log --reverse -1` lies).
    with tempfile.TemporaryDirectory() as repo:
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@e",
                   GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@e")

        def git(*args, **kw):
            subprocess.run(["git"] + list(args), cwd=repo, env=env,
                           capture_output=True, check=True, **kw)

        try:
            git("init", "-q")
        except (subprocess.SubprocessError, OSError):
            print("scan_capstone selftest: git unavailable, skipped git ordering check")
        else:
            write(f"{repo}/a.txt", "one\n")
            git("add", "-A")
            git("commit", "-q", "-m", "first", "--date=2020-01-01T00:00:00Z")
            write(f"{repo}/b.txt", "two\n")
            git("add", "-A")
            git("commit", "-q", "-m", "second", "--date=2024-06-01T00:00:00Z")
            g = scan(repo)["git"]
            assert g["commits"] == 2, g
            assert g["first_commit_at"].startswith("2020-01-01"), g
            assert g["last_commit_at"].startswith("2024-06-01"), g

    print("scan_capstone selftest: all assertions passed")
    return 0


def main(argv):
    args = [a for a in argv[1:]]
    if "--selftest" in args:
        return selftest()
    as_json = "--json" in args
    args = [a for a in args if not a.startswith("--")]
    root = args[0] if args else "."
    if not os.path.isdir(root):
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2
    inv = scan(root)
    if as_json:
        print(json.dumps(inv, indent=2, ensure_ascii=False))
    else:
        print(render_summary(inv))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
