from checkQC.qc_checkers.utils import handler2checker

def test_handler2checker():
    assert handler2checker("ErrorRateHandler") == "error_rate"
    assert handler2checker("ClusterPFHandler") == "cluster_pf"
    assert handler2checker("CheckQC") == "check_qc"

    for checker in [
        "error_rate",
        "cluster_pf",
        "check_qc",
    ]:
        assert handler2checker(checker) == checker

