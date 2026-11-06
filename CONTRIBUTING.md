# Contributing

Keep canonical rules in `docs/` and profiles additive. Skills point to canonical rules and describe a focused procedure; they are not copies of policy. Changes that affect installation, discovery, approvals or compatibility need a decision record or a clear PR rationale. Update templates, examples, and affected verification together. Run `python3 scripts/validate.py` and `python3 -m unittest discover -s tests -v`, inspect the diff, and report actual results. Test scripts in disposable directories. Never commit secrets or real customer data.
