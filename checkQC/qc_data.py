import interop
import csv
import pathlib

class QCData:
    def __init__(
        self,
        instrument,
        read_length,
        samplesheet,
        lane_data,  # TODO validate dict content
        # The schema will define mandatory fields but may evolve over time with
        # new instruments
    ):
        self.instrument = instrument
        self.read_length = read_length
        self.samplesheet = samplesheet
        self.lane_data = lane_data

    from checkQC.parsers.illumina import from_bclconvert
