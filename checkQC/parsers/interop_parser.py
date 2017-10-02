
from checkQC.parsers.parser import Parser

from interop import py_interop_run_metrics, py_interop_run, py_interop_summary


class InteropParser(Parser):

    def __init__(self, runfolder, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.runfolder = runfolder

    def run(self):

        run_metrics = py_interop_run_metrics.run_metrics()
        run_metrics.run_info()

        valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
        py_interop_run_metrics.list_summary_metrics_to_load(valid_to_load)
        run_metrics.read(self.runfolder, valid_to_load)

        summary = py_interop_summary.run_summary()
        py_interop_summary.summarize_run_metrics(run_metrics, summary)

        lanes = summary.lane_count()

        for lane in range(lanes):
            for read_nbr in range(summary.size()):
                read = summary.at(read_nbr).at(lane)
                error_rate = read.error_rate().mean()
                q30 = read.percent_gt_q30()
                self._send_to_subscribers(("error_rate", {"lane": lane+1, "read": read_nbr+1, "error_rate": error_rate}))
                self._send_to_subscribers(("percent_q30", {"lane": lane+1, "read": read_nbr+1, "percent_q30": q30}))

    def __eq__(self, other):
        if isinstance(other, self.__class__) and self.runfolder == other.runfolder:
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.__class__.__name__ + self.runfolder)
