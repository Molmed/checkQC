class QCData:
    """
    Represents the data contained in a runfolder.

    Various constructors are available, depending on which demultiplexer
    was used to process the runfolder.
    """
    def __init__(
        self,
        instrument,
        read_length,
        samplesheet,
        sequencing_metrics,  # TODO validate dict content
        # The schema will define mandatory fields but may evolve over time with
        # new instruments
    ):
        self.instrument = instrument
        self.read_length = read_length
        self.samplesheet = samplesheet
        self.sequencing_metrics = sequencing_metrics

    from checkQC.parsers.illumina import from_bclconvert
