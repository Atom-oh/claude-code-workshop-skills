#!/bin/bash
# Tests for marketplace/plugin manifest structure, cross-file consistency, executable
# bits, ${CLAUDE_PLUGIN_ROOT} path resolution, and the co-agent<->kiro verbatim-copied
# script pairs. Logic lives in check_structure.py (JSON/frontmatter parsing is painful
# in bash); this file just feeds its output into the run-all.sh counters.

while IFS=$'\t' read -r status desc detail; do
    if [ "$status" = "PASS" ]; then
        pass "$desc"
    else
        fail "$desc" "$detail"
    fi
done < <(python3 tests/structure/check_structure.py .)
