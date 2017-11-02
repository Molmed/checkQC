
import logging
import logging.config
import os

import click

import tornado.ioloop
import tornado.web
from tornado.gen import coroutine
from tornado.web import url

from checkQC.app import App
from checkQC.config import ConfigFactory

log = logging.getLogger(__name__)


class CheckQCHandler(tornado.web.RequestHandler):

    def initialize(self, **kwargs):
        self.monitor_path = kwargs["monitoring_path"]
        self.qc_config_file = kwargs["qc_config_file"]

    def get(self, runfolder):
        path_to_runfolder = os.path.join(self.monitor_path, runfolder)
        checkqc_app = App(config_file=self.qc_config_file, runfolder=path_to_runfolder)
        reports = checkqc_app.configure_and_run()
        self.set_header("Content-Type", "application/json")
        self.write(reports)


class WebApp(object):

    def __init__(self):
        pass

    def _make_app(self, debug=False, **kwargs):
        routes = [url(r"/([^/]+)", CheckQCHandler, name="checkqc", kwargs=kwargs)]

        return tornado.web.Application(routes, debug=debug)

    def start_web_app(self, monitoring_path, port, config_file, log_config, debug):
        logging_config_path = ConfigFactory.get_logging_config_file(log_config)
        logging.config.dictConfig(logging_config_path)

        log.info("Starting checkqc-ws at port: {}".format(port))

        web_app = self._make_app(monitoring_path=monitoring_path, qc_config_file=config_file, debug=debug)
        web_app.listen(port)
        tornado.ioloop.IOLoop.current().start()


@click.command("checkqc-ws")
@click.argument('monitor_path', type=click.Path())
@click.option("--port", help="Port which checkqc-ws will listen to (default: 9999).", type=click.INT, default=9999)
@click.option("--config", help="Path to the checkQC configuration file", type=click.Path())
@click.option("--log_config", help="Path to the checkQC logging configuration file", type=click.Path())
@click.option('--debug', is_flag=True, default=False, help="Enable debug mode.")
def start(monitor_path, port=9999, config=None, log_config=None, debug=False):
    webapp = WebApp()
    webapp.start_web_app(monitor_path, port, config, log_config, debug)
