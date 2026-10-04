"""Command line interface: `python -m promptguard.cli run suite.json`."""
from __future__ import annotations
import argparse, sys
from .providers import get_provider
from . import runner


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="promptguard", description="Regression-test your LLM prompts")
    ap.add_argument("command", choices=["run", "baseline"])
    ap.add_argument("suite")
    ap.add_argument("--provider", default="mock", choices=["mock", "anthropic"])
    ap.add_argument("--model")
    a = ap.parse_args(argv)

    suite = runner.load_suite(a.suite)
    provider = get_provider(a.provider, replies=suite.get("mock_replies"), model=a.model)
    bpath = runner.baseline_path(a.suite)

    if a.command == "baseline":
        results = runner.run_suite(suite, provider)
        runner.save_baseline(bpath, results)
        print(f"Saved baseline for {len(results)} cases -> {bpath}")
        return 0

    results = runner.run_suite(suite, provider, runner.load_baseline(bpath))
    print(runner.report(results))
    return 0 if all(r.passed for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
