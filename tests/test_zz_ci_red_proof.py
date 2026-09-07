"""SCRATCH: deliberate test failure to prove the Tests job can go red.

Collection must SUCCEED so the job log reads "14 passed, 1 failed" -- proof
that the real suite executed. A collection error would prove nothing.
"""


def test_zz_ci_red_proof_deliberate_failure() -> None:
    assert 1 == 2, "deliberate failure: proving the Tests job can go red"
