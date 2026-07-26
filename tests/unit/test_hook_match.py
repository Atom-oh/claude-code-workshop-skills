#!/usr/bin/env python3
"""Assert-based table tests for hook_match.py — the pre-commit-review PreToolUse hook's
`git commit` matcher. This is this repo's highest-risk untested code: pure regex
gate-keeping over shell command text, blocking (or skipping) real commits, with every
edge case documented in the module's own docstring but never exercised. Cases below are
lifted straight from those docstrings.

Usage: python3 tests/unit/test_hook_match.py   (exit 0 = all passed)
"""
import importlib.util
import os
import sys

_HOOK_MATCH = os.path.join(
    os.path.dirname(__file__), "..", "..",
    "plugins", "kiro", "skills", "kiro-delegate", "scripts", "hook_match.py")

spec = importlib.util.spec_from_file_location("hook_match", _HOOK_MATCH)
hook_match = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook_match)


def check(fn, cmd, expected, label):
    actual = fn(cmd)
    assert actual == expected, f"{label}: {fn.__name__}({cmd!r}) = {actual}, expected {expected}"


CASES = [
    # (function, command, expected, label)
    (hook_match.is_git_commit, "git commit -m x", True, "plain commit"),
    (hook_match.is_git_commit, 'echo "git commit"', False, "quoted string, not a real invocation"),
    (hook_match.is_git_commit, "cat <<'EOF' > f\ngit commit inside heredoc\nEOF", False,
     "heredoc body is inert data, not a real invocation"),
    (hook_match.is_git_commit, "git commit-tree abc123", False,
     "commit-tree is a different subcommand, must not match as a commit prefix"),
    (hook_match.is_git_commit, "git --git-dir foo commit -m x", True,
     "separate-value --git-dir before commit must still match"),
    (hook_match.is_git_commit, "KIRO_REVIEW=off git commit -m x", True,
     "env-var prefix before git must not block the match"),

    (hook_match.is_scope_mismatch, "git -C /elsewhere commit -m x", True,
     "-C before commit redirects the target repo"),
    (hook_match.is_scope_mismatch, "git commit -am x", True,
     "-a widens scope even bundled in a short-flag cluster"),
    (hook_match.is_scope_mismatch, "git commit path/to/file", True,
     "trailing pathspec narrows the commit to one file"),
    (hook_match.is_scope_mismatch, 'git commit -m "message text"', False,
     "a quoted -m message must not be mistaken for a pathspec"),
    (hook_match.is_scope_mismatch, "git commit -m x", False, "plain commit has no mismatch"),

    (hook_match.is_stale_index, "git add x && git commit -m y", True,
     "an index mutation before commit makes the reviewed diff stale"),
    (hook_match.is_stale_index, "git commit -m y", False, "no preceding index mutation"),

    (hook_match.is_multi_commit, "git commit -m x && git add y && git commit -m z", True,
     "two separate commit invocations in one command"),
    (hook_match.is_multi_commit, "git commit -m x", False, "single commit invocation"),

    (hook_match.is_bypassed, "KIRO_REVIEW=off git commit -m x", True,
     "inline bypass assignment immediately before git"),
    (hook_match.is_bypassed, "NOTE=KIRO_REVIEW=off git commit -m x", False,
     "KIRO_REVIEW=off here is the VALUE of NOTE, not its own env assignment"),
    (hook_match.is_bypassed, "git commit -m x", False, "no bypass assignment present"),
]


def main():
    failures = []
    for fn, cmd, expected, label in CASES:
        try:
            check(fn, cmd, expected, label)
        except AssertionError as e:
            failures.append(str(e))
    if failures:
        print(f"{len(failures)}/{len(CASES)} FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print(f"{len(CASES)}/{len(CASES)} passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
