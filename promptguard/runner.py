"""Suite loading, execution, baseline storage and reporting."""
from __future__ import annotations
import json, pathlib
from dataclasses import dataclass, field
from .assertions import check
from .providers import get_provider


@dataclass
class CaseResult:
    id: str
    passed: bool
    output: str
    failures: list[str] = field(default_factory=list)


def load_suite(path: str) -> dict:
    suite = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    if "cases" not in suite or not suite["cases"]:
        raise ValueError("suite needs a non-empty 'cases' list")
    return suite


def render(template: str, variables: dict) -> str:
    for k, v in variables.items():
        template = template.replace("{{" + k + "}}", str(v))
    return template


def baseline_path(suite_path: str) -> pathlib.Path:
    p = pathlib.Path(suite_path)
    return p.with_suffix(".baseline.json")


def run_suite(suite: dict, provider, baselines: dict | None = None) -> list[CaseResult]:
    baselines = baselines or {}
    results = []
    for case in suite["cases"]:
        prompt = render(suite.get("prompt", "{{input}}"), case.get("vars", {}))
        out = provider.complete(prompt)
        failures = []
        for a in case.get("assertions", []):
            ok, desc = check(a, out, baselines.get(case["id"]))
            if not ok:
                failures.append(desc)
        results.append(CaseResult(case["id"], not failures, out, failures))
    return results


def save_baseline(path: pathlib.Path, results: list[CaseResult]) -> None:
    path.write_text(json.dumps({r.id: r.output for r in results}, indent=2), encoding="utf-8")


def load_baseline(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def report(results: list[CaseResult]) -> str:
    lines = []
    for r in results:
        lines.append(f"{'PASS' if r.passed else 'FAIL'}  {r.id}")
        for f in r.failures:
            lines.append(f"        - failed: {f}")
    p = sum(r.passed for r in results)
    lines.append(f"\n{p}/{len(results)} passed")
    return "\n".join(lines)
