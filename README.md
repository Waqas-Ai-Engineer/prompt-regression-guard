# promptguard

**Regression tests for LLM prompts.** Change a prompt or swap a model, and know in seconds whether your outputs still behave. Zero dependencies (stdlib only), CI-friendly exit codes, and an offline mock provider so tests need no API key.

## Why
Prompts break silently. Teams ship a "small wording tweak" and support answers change tone, drop a policy fact, or blow past length limits. `promptguard` treats prompts like code: a JSON test suite, assertions, and baselines you can diff.

## Features
- JSON suites with `{{variable}}` templating
- Assertions: `contains`, `not_contains`, `regex`, `max_words`, `min_words`, `is_json`, `similar_to_baseline`
- Baselines: snapshot known-good outputs, then fail when new output drifts below a similarity threshold
- Providers: deterministic `mock` (offline) and `anthropic` (set `ANTHROPIC_API_KEY`)
- Exit code `1` on any failure, so it drops straight into GitHub Actions

## Quick start
```bash
python -m promptguard.cli baseline examples/support_bot.json   # snapshot good outputs
python -m promptguard.cli run examples/support_bot.json        # run the checks
python -m promptguard.cli run examples/support_bot.json --provider anthropic --model claude-haiku-4-5
```
Example output:
```
PASS  refund-policy
PASS  password-reset
PASS  cancel-upsell

3/3 passed
```

## Suite format
```json
{
  "prompt": "You are a support agent. Customer: {{input}}",
  "cases": [
    {"id": "refund", "vars": {"input": "How long is a refund?"},
     "assertions": [{"type": "contains", "value": "5 business days"},
                    {"type": "max_words", "value": 40}]}
  ]
}
```
The optional `mock_replies` map (substring -> reply) drives the offline provider.

## CI example
```yaml
- run: python -m promptguard.cli run prompts/support.json --provider anthropic
  env: { ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }} }
```

## Tests
```bash
pip install -r requirements.txt && pytest
```

## Roadmap
OpenAI provider, LLM-as-judge assertion, HTML report, cost/latency tracking.

## License
MIT
