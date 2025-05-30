
from checkQC.handlers.qc_handler import QCHandler, QCErrorFatal, QCErrorWarning
from checkQC.parsers.interop_parser import InteropParser
from checkQC.exceptions import ConfigurationError


class ErrorRateHandler(QCHandler):
    """
    This handler will check that the error rate per lane and read are below the specified threshold.
    Sometimes an error rate estimate is not available, e.g. when no PhiX has been included on
    the lane which is being analyzed. If you want to allow this to pass anyway, ensure that the
    ErrorRateHandler has 'allow_missing_error_rate' set to 'True'.
    """

    ALLOW_MISSING_ERROR_RATE = "allow_missing_error_rate"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_results = []

    def parser(self):
        """
        The ErrorRateHandler fetches its data from the Interop files.

        :returns: an InteropParser callable
        """
        return InteropParser

    def collect(self, signal):
        key, value = signal
        if key == "error_rate":
            self.error_results.append(value)

    def custom_configuration_validation(self):
        try:
            value = self.qc_config[self.ALLOW_MISSING_ERROR_RATE]
        except KeyError as e:
            raise ConfigurationError("Did not find key '{}' in configuration for ErrorRate handler".format(e.args[0]))

        if not isinstance(value, bool):
            raise ConfigurationError("Only True/False are allowed as values for 'allow_missing_error_rate' in the "
                                     "ErrorRate handler config. Value was: {}".format(value))

    def check_qc(self):
        # error_rate handler is not supposed to handle index reads.
        for error_dict in filter(lambda x: not x["is_index_read"], self.error_results):
            lane_nbr = int(error_dict["lane"])
            read = error_dict["read"]
            error_rate = error_dict["error_rate"]
            is_index_read = error_dict.get("is_index_read", False)

            if error_rate == 0 and not self.qc_config[self.ALLOW_MISSING_ERROR_RATE]:
                yield QCErrorFatal(
                    f"Error rate was found to be 0 on lane: {lane_nbr} for read: "
                    f"{read}, this is probably because there was no PhiX loaded "
                    f"on this lane. If do not use PhiX for your runs you can "
                    f"set 'allow_missing_error_rate' in the config to True, "
                    f"which will remove the messages in the future.")
            elif self.error() != self.UNKNOWN and error_rate > self.error():
                yield QCErrorFatal(
                    f"Error rate {error_rate} was to high on lane: {lane_nbr} "
                    f"for read: {read}",
                    ordering=lane_nbr,
                    data={
                        "lane": lane_nbr,
                        "read": read,
                        "error_rate": error_rate,
                        "threshold": self.error()
                    }
                )
            elif self.warning() != self.UNKNOWN and error_rate > self.warning():
                yield QCErrorWarning(
                    f"Error rate {error_rate} was to high on lane: {lane_nbr} "
                    f"for read: {read}",
                    ordering=lane_nbr,
                    data={
                        "lane": lane_nbr,
                        "read": read,
                        "error_rate": error_rate,
                        "threshold": self.warning()
                    }
                )
            else:
                continue

