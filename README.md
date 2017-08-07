checkQC
=======
[![Build Status](https://travis-ci.org/Molmed/checkQC.svg?branch=master)](https://travis-ci.org/Molmed/checkQC)
[![codecov](https://codecov.io/gh/Molmed/checkQC/branch/master/graph/badge.svg)](https://codecov.io/gh/Molmed/checkQC)

**NOTICE**<br>
This is is pre-alpha stage software, it is not yet ready for any kind of real usage.
Please return once we have a release. :D

`checkQC` is a program designed to check a set of quality criteria against an Illumina runfolder. It has been designed
to be modular, and exactly which "qc handlers" are executed with which parameters for a specific run type (i.e. machine
type and run length) is determined by a configuration file.

Install instructions
--------------------

TODO: Note that this is still a work in progress description
```
pip install -f https://github.com/Illumina/interop/releases/latest interop
pip install checkQC
```

Running in a Singularity container
----------------------------------

[Singularity](http://singularity.lbl.gov/index.html) is a container system focusing on scientific use cases. 
`checkQC` can be run in a Singularity container by first creating a container using the following:

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

`checkQC` attempts to be as modular as possible, with respect to adding support for reading more file types (via
the implementation of new parsers) and QC criteria (via the implementation of new handlers).

Once `checkQC` starts it will read the configuration file provided, and based on the run type of being analyzed, it will
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
