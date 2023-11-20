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
from gevent.pywsgi import WSGIServer

from app import Main
from config import ServerType


class StatusServer:
    def __init__(self, main: Main):
        self.__logger = logging.getLogger("Server")
        logging.basicConfig(level=logging.INFO)
        self.__logger.info("Initializing Web API...")

        self.app = Flask(__name__)

        self.__config = main.config
        self.__status = main.status

        self.host = self.__config.web_server.host
        self.port = self.__config.web_server.port

        if self.__config.server_type == ServerType.MAIN:
            self.__status.update_nodes(self.__config.nodes, True)
            threading.Timer(self.__config.refresh_interval, self.refresh).start()
        else:
            self.__status.set_node_mode()

        self.telegram = main.telegram

        # api methods
        @self.app.route('/', methods=['GET'])
        def index() -> str:
            return "You've entered jimchen5209's status api."

        @self.app.route('/getStatus', methods=['GET'])
        def get_status() -> dict:
            return self.__status.get_status()

        @self.app.route('/getStatus/refreshNow', methods=['GET'])
        def update_and_get_status() -> dict:
            self.__status.update_status()
            return self.__status.get_status()

    def refresh(self):
        self.__logger.info("Auto refreshing...")
        self.__status.update_status()
        threading.Timer(self.__config.refresh_interval, self.refresh).start()

    def start_server(self):
        self.__logger.info("Stating Web Server...")
        http_server = WSGIServer((self.host, self.port), self.app)
        self.__logger.info("Listening on http://{host}:{port}/".format(host=self.host, port=self.port))
        http_server.serve_forever()
