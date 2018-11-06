

"""
Collecting handled Exceptions used by CheckQC.
"""


class CheckQCException(Exception):
    pass


class ConfigurationError(CheckQCException):
    pass


class InstrumentTypeUnknown(ConfigurationError):
    pass


class RunModeUnknown(ConfigurationError):
    pass


class ReagentVersionUnknown(ConfigurationError):
    pass


class RunInfoXMLNotFound(CheckQCException):
    pass


class DemuxSummaryNotFound(CheckQCException):
    pass


class RunParametersNotFound(CheckQCException):
    pass


class StatsJsonNotFound(CheckQCException):
    pass


class QCHandlerNotFound(CheckQCException):
    pass


class ConfigurationError(CheckQCException):
    pass


class SamplesheetNotFound(CheckQCException):
    pass


class ConfigEntryMissing(ConfigurationError):
    pass


class RunfolderNotFoundError(CheckQCException):
    pass
