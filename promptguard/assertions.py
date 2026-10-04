"""Assertion types a test case can use."""
from __future__ import annotations
import json, re
from difflib import SequenceMatcher


def check(assertion: dict, output: str, baseline: str | None = None) -> tuple[bool, str]:
    t = assertion["type"]
    v = assertion.get("value")
    if t == "contains":
        return v.lower() in output.lower(), f"contains {v!r}"
    if t == "not_contains":
        return v.lower() not in output.lower(), f"not_contains {v!r}"
    if t == "regex":
        return re.search(v, output, re.I | re.S) is not None, f"regex {v!r}"
    if t == "max_words":
        n = len(output.split())
        return n <= v, f"max_words {v} (got {n})"
    if t == "min_words":
        n = len(output.split())
        return n >= v, f"min_words {v} (got {n})"
    if t == "is_json":
        try:
            json.loads(output)
            return True, "is_json"
        except ValueError:
            return False, "is_json"
    if t == "similar_to_baseline":
        if baseline is None:
            return True, "similar_to_baseline (no baseline yet)"
        ratio = SequenceMatcher(None, baseline, output).ratio()
        return ratio >= v, f"similar_to_baseline >= {v} (got {ratio:.2f})"
    raise ValueError(f"unknown assertion type: {t}")
