

"""
Collecting handled Exceptions used by CheckQC.
"""


class CheckQCException(Exception):
    pass


class InstrumentTypeUnknown(CheckQCException):
    pass


class RunModeUnknown(CheckQCException):
    pass


class ReagentVersionUnknown(CheckQCException):
    pass


class RunInfoXMLNotFound(CheckQCException):
    pass


class RunParametersNotFound(CheckQCException):
    pass


class StatsJsonNotFound(CheckQCException):
    pass
