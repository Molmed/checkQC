
import logging
import logging.config
import os
from concurrent.futures import ProcessPoolExecutor

import click

import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado.gen import coroutine
from tornado.web import url

from checkQC.app import App
from checkQC.config import ConfigFactory

log = logging.getLogger(__name__)

from checkQC import __version__ as checkqc_version

class CheckQCHandler(tornado.web.RequestHandler):

    # To make the ProcessPoolExecutor and Tornado play well together, this needs to be
    # set after the server has been started. This is kind of hacky, but it appears to work
    # well enough for now. An explanation of the problem is available here:
    # https://stackoverflow.com/questions/26370139/tornado-concurrency-errors-running-multiple-processes-together-with-a-process-po/26370643#26370643
    # / JD 2017-11-08
    process_pool = None

    def initialize(self, **kwargs):
        self.monitor_path = kwargs["monitoring_path"]
        self.qc_config_file = kwargs["qc_config_file"]

    @staticmethod
    def _run_check_qc(monitor_path, qc_config_file, runfolder):
        path_to_runfolder = os.path.join(monitor_path, runfolder)
        checkqc_app = App(config_file=qc_config_file, runfolder=path_to_runfolder)
        reports = checkqc_app.configure_and_run()
        reports["version"] = checkqc_version
        return reports

    @coroutine
    def get(self, runfolder):
        reports = yield self.process_pool.submit(self._run_check_qc, self.monitor_path, self.qc_config_file, runfolder)
        self.set_header("Content-Type", "application/json")
        self.write(reports)


class WebApp(object):

    def __init__(self):
        pass

    @staticmethod
    def _routes(**kwargs):
        return [url(r"/qc/([^/]+)", CheckQCHandler, name="checkqc", kwargs=kwargs)]

    @staticmethod
    def _make_app(debug=False, **kwargs):
        return tornado.web.Application(WebApp._routes(**kwargs), debug=debug)

    @staticmethod
    def _create_server(port, app):
        server = tornado.httpserver.HTTPServer(app)
        server.bind(port)
        return server

    def start_web_app(self, monitoring_path, port, config_file, log_config, debug):
        logging_config_path = ConfigFactory.get_logging_config_dict(log_config)
        logging.config.dictConfig(logging_config_path)

        log.info("Starting checkqc-ws at port: {}".format(port))

        # See the comment above in the CheckQCHandler as to why this somewhat backward way
        # is used to setup the server and ProcessPoolExecutor. /JD 2017-11-08
        web_app = self._make_app(monitoring_path=monitoring_path, qc_config_file=config_file, debug=debug)
        server = self._create_server(port=port, app=web_app)
        server.start()
        CheckQCHandler.process_pool = ProcessPoolExecutor()
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
