#!/bin/bash
# Wraps test_hook_match.py (assert-based) into the run-all.sh counters.

OUTPUT=$(python3 tests/unit/test_hook_match.py 2>&1)
STATUS=$?
if [ "$STATUS" -eq 0 ]; then
    pass "hook_match.py: $OUTPUT"
else
    fail "hook_match.py table tests" "$OUTPUT"
fi
