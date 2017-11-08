checkQC
=======
[![Build Status](https://travis-ci.org/Molmed/checkQC.svg?branch=master)](https://travis-ci.org/Molmed/checkQC)
[![codecov](https://codecov.io/gh/Molmed/checkQC/branch/master/graph/badge.svg)](https://codecov.io/gh/Molmed/checkQC)

CheckQC is a program designed to check a set of quality criteria against an Illumina runfolder.

This is useful as part of a pipeline, where one needs to evaluate a set of quality criteria after demultiplexing. CheckQC is fast, and
should finish a few seconds. It will warn if there are problems breaching warning criteria, and will emit a non-zero exit status if it finds
any errors, thus making it easy to stop further processing if the run that is being evaluated needs troubleshooting.

CheckQC has been designed to be modular, and exactly which "qc handlers" are executed with which parameters for a specific run type (i.e. machine
type and run length) is determined by a configuration file.

Instrument types supported in checkQC are the following:
 - HiSeqX
 - HiSeq2500
 - MiSeq
 - NovaSeq

Install instructions
--------------------
Right now the Illumina Interop library needs to be installed separately before moving on to
installing checkqc.

```
pip install -f https://github.com/Illumina/interop/releases/tag/v1.1.1 interop
pip install checkqc
```

Running CheckQC
---------------

After installing CheckQC you can run it by specifying the path to the runfolder you want to
analyze like this:

```
checkqc <RUNFOLDER>
```

This will use the default configuration file packaged with CheckQC if you want to specify
your own custom file, you can do so by adding a path to the config like this:

```
checkqc --config_file <path to your config> <RUNFOLDER>
```

When CheckQC starts and no path to the config file is specified it will give you
the path to where the default file is located on your system, if you want a template
that you can customize according to your own needs.

Running CheckQC as a webservice
-------------------------------

In addition to running like a commandline application, CheckQC can be run as a simple webservice.

To run it you simply need to provide the path to a directory where runfolders that you want to
be able to check are located. This is given as `MONITOR_PATH` below. There are also a number
of optional arguments that can be passed to the service.

```
$ checkqc-ws --help
Usage: checkqc-ws [OPTIONS] MONITOR_PATH

Options:
  --port INTEGER     Port which checkqc-ws will listen to (default: 9999).
  --config PATH      Path to the checkQC configuration file (optional)
  --log_config PATH  Path to the checkQC logging configuration file (optional)
  --debug            Enable debug mode.
  --help             Show this message and exit.

```

Once the webserver is running you can query the `/qc/` endpoint and get any errors and warnings back as json.
Here is an example how to query the endpoint, and what type of results it will return:

```
$ curl -s -w'\n' localhost:9999/qc/170726_D00118_0303_BCB1TVANXX | python -m json.tool
{
    "ClusterPFHandler": [
        {
            "data": {
                "lane": 1,
                "lane_pf": 117929896,
                "threshold": 180
            },
            "message": "Cluster PF was to low on lane 1, it was: 117.93 M",
            "type": "warning"
        },
        {
            "data": {
                "lane": 7,
                "lane_pf": 122263375,
                "threshold": 180
            },
            "message": "Cluster PF was to low on lane 7, it was: 122.26 M",
            "type": "warning"
        },
        {
            "data": {
                "lane": 8,
                "lane_pf": 177018999,
                "threshold": 180
            },
            "message": "Cluster PF was to low on lane 8, it was: 177.02 M",
            "type": "warning"
        }
    ],
    "ReadsPerSampleHandler": [
        {
            "data": {
                "lane": 7,
                "number_of_samples": 12,
                "sample_id": "Sample_pq-27",
                "sample_reads": 6.893002,
                "threshold": 90
            },
            "message": "Number of reads for sample Sample_pq-27 was too low on lane 7, it was: 6.893 M",
            "type": "warning"
        },
        {
            "data": {
                "lane": 7,
                "number_of_samples": 12,
                "sample_id": "Sample_pq-28",
                "sample_reads": 7.10447,
                "threshold": 90
            },
            "message": "Number of reads for sample Sample_pq-28 was too low on lane 7, it was: 7.104 M",
            "type": "warning"
        }
    ],
    "exit_status": 0,
    "version": "1.1.0"
}
```




Running in a Singularity container
----------------------------------

[Singularity](http://singularity.lbl.gov/index.html) is a container system focusing on scientific use cases. 
CheckQC can be run in a Singularity container by first creating a container using the following:

```
singularity create checkQC.img
sudo singularity bootstrap checkQC.img Singularity
```

And then the program itself can be run in the following way:

```
singularity run checkQC.img tests/resources/MiSeqDemo/
```


General architecture notes
--------------------------

CheckQC attempts to be as modular as possible, with respect to adding support for reading more file types (via
the implementation of new parsers) and QC criteria (via the implementation of new handlers).

Once CheckQC starts it will read the configuration file provided, and based on the run type of being analyzed, it will
determine which handlers should be run, and with which parameters. The handlers specify which parser they require
and a single instance of each such parser will be instantiated (i.e. if multiple handlers use the same parser, there
should still only be a single parser instance of that type present). The handlers are then subscribed to events
emitted by the parsers, which send such events to their subscribers as they gather data. Finally once all parsers have
finished collecting data, each handler is requested to report back on if the specified QC criteria were met or not.


Adding new handlers
-------------------

To add a new handler type you need to create a subtype of the `QCHandler` class and place it under the `checkQC/handlers`
directory. Lets have a look at how to implement such a class. Here are the methods that need to be implemented, and a
scaffold for the class

```
class MyQCHandler(QCHandler):

    def __init__(self, qc_config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.qc_config = qc_config

    def parser(self, runfolder):
        pass

    def collect(self, signal):
        pass

    def check_qc(self):
        pass
```

The `parser` method determines which type of files in the runfolder that this handler wants its information from. If
you e.g. want to make it pick up information from the `Stats.json` file, give it a `StatsJsonParser` class, i.e.

```
    def parser(self, runfolder):
        return StatsJsonParser
```

Once the program has set up and begins to execute, the parsers will send information to all the handlers which are
interested in their data. In order for a handler to determine which information it wants to pick up, it needs to
implement a `collect method`. The collect method takes a `signal` as a parameter, and in the case of a `Stats.json`
dependent handler this signal will consist of a key-value pair for each top level key-value pair in the json file.
This means that you need to decide which values to pick up. This can e.g. look something like this:

```
    def collect(self, signal):
        key, value = signal
        if key == "ConversionResults":
            self.conversion_results = value
```

This will pick up the `ConversionResults` key for later processing.

Finally you need to implement the `check_qc` method. This is where the QC metrics are actually checked, and depending
on which values they take the method should `yield` and instance of `QCErrorFatal` or `QCErrorWarning`, depending on the
severity of the problem. Here is an example:

```
    def check_qc(self):
        for lane_dict in self.conversion_results:
            lane_nbr = lane_dict["LaneNumber"]
            lane_yield = lane_dict["Yield"]

            if lane_yield < float(self.qc_config["error"]) * pow(10, 9):
                yield QCErrorFatal("Yield was to low on lane {}, it was: {}".format(lane_nbr, lane_yield))
            elif lane_yield < float(self.qc_config["warning"]) * pow(10, 9):
                yield QCErrorWarning("Yield was to low on lane {}, it was: {}".format(lane_nbr, lane_yield))
            else:
                continue
```

An example of what a full `QCHandler` class might look like can be found below, and more examples are found in the
`checkQC/handlers/` directory.

```
class MyQCHandler(QCHandler):

    def __init__(self, qc_config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversion_results = None
        self.qc_config = qc_config

    def parser(self, runfolder):
        return StatsJsonParser

    def collect(self, signal):
        key, value = signal
        if key == "ConversionResults":
            self.conversion_results = value

    def check_qc(self):
        for lane_dict in self.conversion_results:
            lane_nbr = lane_dict["LaneNumber"]
            lane_yield = lane_dict["Yield"]

            if lane_yield < float(self.qc_config["error"]) * pow(10, 9):
                yield QCErrorFatal("Yield was to low on lane {}, it was: {}".format(lane_nbr, lane_yield))
            elif lane_yield < float(self.qc_config["warning"]) * pow(10, 9):
                yield QCErrorWarning("Yield was to low on lane {}, it was: {}".format(lane_nbr, lane_yield))
            else:
                continue
```

Upload to PyPi
--------------
TODO: This has only been tested for pypitest so far, but everything appears to be working so far. Rewrite this
once a real version has been deployed to PyPi.

First create a `~/.pypirc` file with your PyPi credentials, and then run:

```
python setup.py sdist bdist_wheel
twine upload -r pypitest dist/*
```
