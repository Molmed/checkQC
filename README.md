checkQC
=======
[![Build Status](https://travis-ci.org/Molmed/checkQC.svg?branch=master)](https://travis-ci.org/Molmed/checkQC)
[![codecov](https://codecov.io/gh/Molmed/checkQC/branch/master/graph/badge.svg)](https://codecov.io/gh/Molmed/checkQC)
[![PyPI](https://img.shields.io/pypi/v/checkqc.svg)](https://pypi.python.org/pypi/checkQC)
[![Conda](https://img.shields.io/conda/v/bioconda/checkqc)](https://anaconda.org/bioconda/checkqc)
[![Documentation Status](https://readthedocs.org/projects/checkqc/badge/?version=latest)](http://checkqc.readthedocs.io/en/latest/?badge=latest)
[![DOI](http://joss.theoj.org/papers/10.21105/joss.00556/status.svg)](https://doi.org/10.21105/joss.00556)

More documentation is available at [http://checkqc.readthedocs.io/](http://checkqc.readthedocs.io/en/latest/)

CheckQC is a program designed to check a set of quality criteria against an Illumina runfolder.

This is useful as part of a pipeline, where one needs to evaluate a set of quality criteria after demultiplexing. CheckQC is fast, and
should finish within a few seconds. It will warn if there are problems breaching warning criteria, and will emit a non-zero exit status if it finds
any errors, thus making it easy to stop further processing if the run that is being evaluated needs troubleshooting.

CheckQC has been designed to be modular, and exactly which "qc handlers" are executed with which parameters for a specific run type (i.e. machine
type and run length) is determined by a configuration file.

Instrument types supported in checkQC are the following:
 - HiSeqX
 - HiSeq2500
 - iSeq
 - MiSeq
 - NovaSeq
 - NovaSeq X Plus

Install instructions
--------------------
CheckQC requires **Python 3.10**. CheckQC can be installed with pip.

```
pip install checkqc
```

Alternatively it can be installed with conda using the bioconda channel:

```
conda install -c bioconda checkqc
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

When you run CheckQC you can expect to see output similar to this:

```
checkqc  tests/resources/170726_D00118_0303_BCB1TVANXX/
INFO     ------------------------
INFO     Starting checkQC (1.1.2)
INFO     ------------------------
INFO     Runfolder is: tests/resources/170726_D00118_0303_BCB1TVANXX/
INFO     No config file specified, using default config from /home/MOLMED/johda411/workspace/checkQC/checkQC/default_config/config.yaml.
INFO     Run summary
INFO     -----------
INFO     Instrument and reagent version: hiseq2500_rapidhighoutput_v4
INFO     Read length: 125-125
INFO     Enabled handlers and their config values were:
INFO            ClusterPFHandler Error=unknown Warning=180
INFO            Q30Handler Error=unknown Warning=80
INFO            ErrorRateHandler Error=unknown Warning=2
INFO            ReadsPerSampleHandler Error=90 Warning=unknown
INFO            UndeterminedPercentageHandler Error=10 Warning=unknown
WARNING  QC warning: Cluster PF was to low on lane 1, it was: 117.93 M
WARNING  QC warning: Cluster PF was to low on lane 7, it was: 122.26 M
WARNING  QC warning: Cluster PF was to low on lane 8, it was: 177.02 M
ERROR    Fatal QC error: Number of reads for sample Sample_pq-27 was too low on lane 7, it was: 6.893 M
ERROR    Fatal QC error: Number of reads for sample Sample_pq-28 was too low on lane 7, it was: 7.104 M
INFO     Finished with fatal qc errors and will exit with non-zero exit status.
```

The program will summarize the type of run it has identified and output any warnings and/or errors in finds.
If any qc errors were found the CheckQC will output a non-zero exit status. This means it can easily be used to
decide if a further steps should run or not, e.g. in a workflow.

In addition to the normal output CheckQC has a json mode, enabled by adding `--json` to the commandline.
This outputs the results normally shown in the log as json on `stdout` (while the log itself is written to `stderr`),
so that this can either be written to a file, or redirected to other programs which can parse the data further.
In this example we use the python json tool to pretty print the json output:

```
checkqc --json tests/resources/170726_D00118_0303_BCB1TVANXX/  | python -m json.tool
INFO     ------------------------
INFO     Starting checkQC (1.1.2)
INFO     ------------------------
INFO     Runfolder is: tests/resources/170726_D00118_0303_BCB1TVANXX/
INFO     No config file specified, using default config from /home/MOLMED/johda411/workspace/checkQC/checkQC/default_config/config.yaml.
INFO     Run summary
INFO     -----------
INFO     Instrument and reagent version: hiseq2500_rapidhighoutput_v4
INFO     Read length: 125-125
INFO     Enabled handlers and their config values were:
INFO     	ClusterPFHandler Error=unknown Warning=180
INFO     	Q30Handler Error=unknown Warning=80
INFO     	ErrorRateHandler Error=unknown Warning=2
INFO     	ReadsPerSampleHandler Error=90 Warning=unknown
INFO     	UndeterminedPercentageHandler Error=10 Warning=unknown
WARNING  QC warning: Cluster PF was to low on lane 1, it was: 117.93 M
WARNING  QC warning: Cluster PF was to low on lane 7, it was: 122.26 M
WARNING  QC warning: Cluster PF was to low on lane 8, it was: 177.02 M
ERROR    Fatal QC error: Number of reads for sample Sample_pq-27 was too low on lane 7, it was: 6.893 M
ERROR    Fatal QC error: Number of reads for sample Sample_pq-28 was too low on lane 7, it was: 7.104 M
INFO     Finished with fatal qc errors and will exit with non-zero exit status.
{
    "exit_status": 1,
    "ClusterPFHandler": [
        {
            "type": "warning",
            "message": "Cluster PF was to low on lane 1, it was: 117.93 M",
            "data": {
                "lane": 1,
                "lane_pf": 117929896,
                "threshold": 180
            }
        },
        {
            "type": "warning",
            "message": "Cluster PF was to low on lane 7, it was: 122.26 M",
            "data": {
                "lane": 7,
                "lane_pf": 122263375,
                "threshold": 180
            }
        },
        {
            "type": "warning",
            "message": "Cluster PF was to low on lane 8, it was: 177.02 M",
            "data": {
                "lane": 8,
                "lane_pf": 177018999,
                "threshold": 180
            }
        }
    ],
    "ReadsPerSampleHandler": [
        {
            "type": "error",
            "message": "Number of reads for sample Sample_pq-27 was too low on lane 7, it was: 6.893 M",
            "data": {
                "lane": 7,
                "number_of_samples": 12,
                "sample_id": "Sample_pq-27",
                "sample_reads": 6.893002,
                "threshold": 90
            }
        },
        {
            "type": "error",
            "message": "Number of reads for sample Sample_pq-28 was too low on lane 7, it was: 7.104 M",
            "data": {
                "lane": 7,
                "number_of_samples": 12,
                "sample_id": "Sample_pq-28",
                "sample_reads": 7.10447,
                "threshold": 90
            }
        }
    ],
    "run_summary": {
        "instrument_and_reagent_type": "hiseq2500_rapidhighoutput_v4",
        "read_length": "125-125",
        "handlers": [
            {
                "handler": "ClusterPFHandler",
                "error": "unknown",
                "warning": 180
            },
            {
                "handler": "Q30Handler",
                "error": "unknown",
                "warning": 80
            },
            {
                "handler": "ErrorRateHandler",
                "error": "unknown",
                "warning": 2
            },
            {
                "handler": "ReadsPerSampleHandler",
                "error": 90,
                "warning": "unknown"
            },
            {
                "handler": "UndeterminedPercentageHandler",
                "error": 10,
                "warning": "unknown"
            }
        ]
    }
}
```

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
