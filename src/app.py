#!/usr/bin/env python


import logging
import os
import time
import signal
import json
import uuid

import click
import tornado.httpserver
import tornado.ioloop
from tornado_json.application import Application
from tornado.log import enable_pretty_logging
from tornado_json.routes import get_routes

import wlsports.api
import wlsports.db
from wlsports.config import Config


def sig_handler(sig, frame):
    """Handles SIGINT by calling shutdown()"""
    logging.warning('Caught signal: %s', sig)
    tornado.ioloop.IOLoop.instance().add_callback(shutdown)


def shutdown():
    """Waits MAX_WAIT_SECONDS_BEFORE_SHUTDOWN, then shuts down the server"""
    MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 1

    logging.info('Stopping http server')
    http_server.stop()

    logging.info('Will shutdown in %s seconds ...',
                 MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
    io_loop = tornado.ioloop.IOLoop.instance()

    deadline = time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN

    def stop_loop():
        now = time.time()
        if now < deadline and (io_loop._callbacks or io_loop._timeouts):
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()
            logging.info('Shutdown')

    stop_loop()


@click.command()
@click.option('-p', '--port', default=8888, type=int, required=True,
              help="Port to start server on")
@click.option('--db', default="../welikesports.sqlite", type=str, required=True,
              help="Path of database file")
@click.option('--session-timeout-days', default=1, required=True,
              help=("Cookie expiration time in days; can also be set to "
                    "``None`` for session cookies, i.e., cookies that "
                    "expire when browser window is closed."))
@click.option('--cookie-secret', default="", required=True,
              help=("Set this to an empty string to generate a new cookie secret "
                    "each time the server is restarted, or to any string which is "
                    "the cookie secret."))
@click.option('--debug', is_flag=True)
def main(port, db, session_timeout_days, cookie_secret, debug):
    """
    - Get options from config file
    - Gather all routes
    - Create the server
    - Start the server
    """
    global http_server

    enable_pretty_logging()

    # Create application configuration
    app_config = Config(
        port=port,
        db_file=db,
        session_timeout_days=session_timeout_days,
        cookie_secret=cookie_secret,
        debug=debug
    )
    # Configure and initialize database
    if debug:
        wlsports.db.sql_debug(True)
    wlsports.db.database.bind("sqlite", db, create_db=True)
    wlsports.db.database.generate_mapping(create_tables=True)

    settings = dict(
        template_path=os.path.join(
            os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        gzip=True,
        cookie_secret=(cookie_secret if cookie_secret
                       else uuid.uuid4().hex),
        app_config=app_config,
        login_url="/api/auth/playerlogin"
    )

    # Create server
    http_server = tornado.httpserver.HTTPServer(
        Application(
            routes=get_routes(wlsports.api),
            settings=settings,
            db_conn=wlsports.db,
        )
    )
    # Bind to port
    http_server.listen(port)

    # Register signal handlers for quitting
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    # Start IO loop
    tornado.ioloop.IOLoop.instance().start()

    logging.info("Exit...")


if __name__ == '__main__':
    main()
