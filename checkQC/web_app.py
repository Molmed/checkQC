
import logging
import logging.config
import os

import click
import json
from json.decoder import JSONDecodeError

import tornado.ioloop
import tornado.web
from tornado.web import url, HTTPError

from checkQC.app import App
from checkQC.config import ConfigFactory
from checkQC.exceptions import *

log = logging.getLogger(__name__)

from checkQC import __version__ as checkqc_version


class CheckQCHandler(tornado.web.RequestHandler):

    def initialize(self, **kwargs):
        self.monitor_path = kwargs["monitoring_path"]
        self.qc_config_file = kwargs["qc_config_file"]
        self.downgrade_errors_for = ()
        self.use_closest_read_length = False

    @staticmethod
    def _run_check_qc(monitor_path, qc_config_file, runfolder, downgrade_errors_for,
                      use_closest_read_length):
        path_to_runfolder = os.path.join(monitor_path, runfolder)
        checkqc_app = App(config_file=qc_config_file, runfolder=path_to_runfolder,
                          downgrade_errors_for=downgrade_errors_for,
                          use_closest_read_length=use_closest_read_length)
        reports = checkqc_app.configure_and_run()
        reports["version"] = checkqc_version
        return reports

    def _write_error(self, status_code, reason):
        self.set_header("Content-Type", "application/json")
        self.set_status(status_code=status_code)
        self.finish({"reason": reason})

    def get(self, runfolder):
        if "downgrade" in self.request.query_arguments:
            self.downgrade_errors_for = self.get_query_argument("downgrade")
        if "useClosestReadLength" in self.request.query_arguments:
            self.use_closest_read_length = True
        try:
            reports = self._run_check_qc(self.monitor_path, self.qc_config_file,
                                         runfolder, self.downgrade_errors_for,
                                         self.use_closest_read_length)
            self.set_header("Content-Type", "application/json")
            self.write(reports)
        except RunfolderNotFoundError:
            self._write_error(status_code=404, reason="Could not find requested runfolder.")
        except ConfigurationError:
            self._write_error(status_code=500, reason="There is a problem with the qc config. Are you sure the "
                                                      "type of instrument/run configuration on the run you want to "
                                                      "analyze is available in the qc config?")


class WebApp(object):

    def __init__(self):
        pass

    @staticmethod
    def _routes(**kwargs):
        return [url(r"/qc/([^/]+)", CheckQCHandler, name="checkqc", kwargs=kwargs)]

    @staticmethod
    def _make_app(debug=False, **kwargs):
        return tornado.web.Application(WebApp._routes(**kwargs), debug=debug)

    def start_web_app(self, monitoring_path, port, config_file, log_config, debug):
        logging_config_path = ConfigFactory.get_logging_config_dict(log_config)
        logging.config.dictConfig(logging_config_path)

        log.info("Starting checkqc-ws at port: {}".format(port))

        if not os.path.isdir(monitoring_path):
            log.error("{} is not a directory".format(monitoring_path))
            raise AssertionError("{} is not a directory".format(monitoring_path))

        web_app = self._make_app(monitoring_path=monitoring_path, qc_config_file=config_file, debug=debug)
        web_app.listen(port=port)
        tornado.ioloop.IOLoop.instance().start()


@click.command("checkqc-ws")
@click.argument('monitor_path', type=click.Path())
@click.option("--port", help="Port which checkqc-ws will listen to (default: 9999).", type=click.INT, default=9999)
@click.option("--config", help="Path to the checkQC configuration file (optional)", type=click.Path())
@click.option("--log_config", help="Path to the checkQC logging configuration file (optional)", type=click.Path())
@click.option('--debug', is_flag=True, default=False, help="Enable debug mode.")
def start(monitor_path, port=9999, config=None, log_config=None, debug=False):
    webapp = WebApp()
    webapp.start_web_app(monitor_path, port, config, log_config, debug)
