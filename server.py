#  StatusServer by jimchen5209
#  Copyright (C) 2019-2019
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
import logging
import threading

from flask import Flask
from flask_classful import route, FlaskView
from gevent.pywsgi import WSGIServer

from config import Config, ServerType
from status import Status

status = Status()


class StatusServer:
    def __init__(self, config: Config):
        self.__logger = logging.getLogger("Server")
        logging.basicConfig(level=logging.INFO)
        self.__logger.info("Initializing Web API...")
        self.app = Flask(__name__)
        self.__config = config
        self.host = self.__config.web_server.host
        self.port = self.__config.web_server.port
        self.content = FlaskApp()
        self.content.register(self.app, route_base="/")
        if config.server_type == ServerType.MAIN:
            status.update_nodes(config.nodes)
            self.refresh()
        else:
            status.set_node_mode()

    def refresh(self):
        self.__logger.info("Auto refreshing...")
        status.update_status()
        threading.Timer(self.__config.refresh_interval, self.refresh).start()

    def start_server(self):
        self.__logger.info("Stating Web Server...")
        http_server = WSGIServer((self.host, self.port), self.app)
        self.__logger.info("Listening on http://{host}:{port}/".format(host=self.host, port=self.port))
        http_server.serve_forever()


class FlaskApp(FlaskView):
    def __init__(self):
        self.default_methods = ['GET']

    @route('/')
    def index(self) -> str:
        return "You've entered jimchen5209's status api."

    @route('/getStatus')
    def get_status(self) -> dict:
        return status.get_status()

    @route('/getStatus/refreshNow')
    def update_and_get_status(self) -> dict:
        status.update_status()
        return status.get_status()
