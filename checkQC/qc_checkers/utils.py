import re

def handler2checker(s):
    """
    Convert a handler name to it's equivalent QC checker
    Ex:
        - ErrorRateHandler -> error_rate
        - ClusterPFHandler -> cluster_pf
        - CheckQC -> check_qc

    This is used to ensure backward compatibility between the CheckQC v4 and v5

    NB: this method is idempotent, it will not modify qc_checker strings
    Ex: error_rate -> error_rate
    """
    words = [
        mtch.group().lower().replace('_', '')
        for mtch in re.finditer(r"[A-Z]?([a-z0-9]+|[A-Z0-9]+)(?=$|[A-Z]|_)", s)
    ]

    if words[-1] == "handler":
        words.pop()

    return "_".join(words)
