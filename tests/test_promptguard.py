import json
from promptguard import runner, assertions
from promptguard.providers import MockProvider
from promptguard.cli import main


def test_assertions():
    assert assertions.check({"type": "contains", "value": "Hi"}, "oh hi there")[0]
    assert not assertions.check({"type": "not_contains", "value": "x"}, "xyz")[0]
    assert assertions.check({"type": "is_json"}, '{"a":1}')[0]
    assert not assertions.check({"type": "max_words", "value": 2}, "a b c")[0]
    assert not assertions.check({"type": "similar_to_baseline", "value": 0.9}, "totally different", "hello world")[0]


def test_render():
    assert runner.render("Hi {{n}}", {"n": "Bo"}) == "Hi Bo"


def test_regression_detected(tmp_path):
    suite = {"prompt": "{{q}}", "cases": [{"id": "c", "vars": {"q": "refund"},
             "assertions": [{"type": "similar_to_baseline", "value": 0.9}]}]}
    good = MockProvider({"refund": "5 business days"})
    base = {r.id: r.output for r in runner.run_suite(suite, good)}
    bad = MockProvider({"refund": "We never refund anything, goodbye forever."})
    res = runner.run_suite(suite, bad, base)
    assert not res[0].passed


def test_cli_exit_codes(tmp_path, capsys):
    s = tmp_path / "s.json"
    s.write_text(json.dumps({"prompt": "{{i}}", "mock_replies": {"a": "alpha"},
        "cases": [{"id": "x", "vars": {"i": "a"}, "assertions": [{"type": "contains", "value": "alpha"}]}]}))
    assert main(["baseline", str(s)]) == 0
    assert main(["run", str(s)]) == 0
    s.write_text(s.read_text().replace('"alpha"}]', '"zzz"}]'))
    assert main(["run", str(s)]) == 1
