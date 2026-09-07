"""SCRATCH: deliberate lint defect to prove the Lint job can go red.

Not collected by pytest (the test job runs `pytest tests/` only), so this
turns exactly one job red and leaves the others to their own defects.
"""

VALUE = deliberately_undefined_name  # noqa-free on purpose: ruff F821 must fire
