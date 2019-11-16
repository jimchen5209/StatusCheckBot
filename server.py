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

from flask import Flask
from flask_classful import route, FlaskView
from gevent.pywsgi import WSGIServer

import status
from logger import Logger


class StatusServer:
    def __init__(self, host: str, port: int, logger: Logger):
        self.log = logger
        self.log.logger.info("Initializing Web API...")
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.content = FlaskApp()
        self.content.register(self.app, route_base="/")

    def start_server(self):
        self.log.logger.info("Stating Web Server...")
        http_server = WSGIServer((self.host, self.port), self.app)
        self.log.logger.info("Listening on http://{host}:{port}/".format(host=self.host, port=self.port))
        http_server.serve_forever()


class FlaskApp(FlaskView):
    def __init__(self):
        self.data = status.get_status()
        self.default_methods = ['GET']

    @route('/')
    def index(self) -> str:
        return "You've entered jimchen5209's status api."

    @route('/getStatus')
    def get_status(self) -> dict:
        self.data.update(status.get_status())
        return self.data
