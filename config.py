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
import json
import logging
from enum import Enum


class Config:
    def __init__(self, raw_data: dict):
        self.server_type = ServerType[raw_data['server_type']] if 'server_type' in raw_data else ServerType.MAIN
        self.web_server = WebServer(
            host=raw_data['web_server']['host'] if 'host' in raw_data['web_server'] else '0.0.0.0',
            port=raw_data['web_server']['port'] if 'port' in raw_data['web_server'] else 5000
        ) if 'web_server' in raw_data else WebServer()
        self.nodes = raw_data['nodes'] if 'nodes' in raw_data else []
        self.refresh_interval = raw_data['refresh_interval'] if 'refresh_interval' in raw_data else 30.0
        self.telegram_admin = (raw_data['telegram_admin'] if raw_data['telegram_admin'] != -1 else None) \
            if 'telegram_admin' in raw_data else None
        self.telegram_token = (raw_data['telegram_token'] if raw_data['telegram_token'] != '' else None) \
            if 'telegram_token' in raw_data else None

    def to_dict(self) -> dict:
        return {
            '//server_type': 'Type of this server, value: MAIN, NODE',
            'server_type': self.server_type.name,
            '//nodes': 'Server nodes if this is a main server and node server presents',
            'nodes': self.nodes,
            '//web_server': 'Listening web server config',
            'web_server': {
                'host': self.web_server.host,
                'port': self.web_server.port
            },
            '//refresh_interval':'Refresh rate of cached data in seconds',
            'refresh_interval': self.refresh_interval,
            '//telegram_token': 'Token of telegram for notifications and subscriptions',
            'telegram_token': self.telegram_token if self.telegram_token else '',
            '//telegram_admin': 'Admin\'s userID',
            'telegram_admin': self.telegram_admin if self.telegram_admin else -1
        }


class ServerType(Enum):
    MAIN = "main"
    NODE = "mode"


class WebServer:
    def __init__(self, host: str = '0.0.0.0', port: int = 5000):
        self.host = host
        self.port = port


class ConfigManager:
    def __init__(self, testing=False):
        self.__logger = logging.getLogger("Config")
        logging.basicConfig(level=logging.INFO)
        self.__logger.info("Loading Config...")
        if testing:
            self.__logger.info("Testing mode detected, using testing config.")
            self.__configRaw = Config({}).to_dict()
        else:
            try:
                with open('./config.json', 'r') as fs:
                    self.__configRaw = json.load(fs)
            except FileNotFoundError:
                self.__logger.error(
                    "Can't load config.json: File not found.")
                self.__logger.info("Generating empty config...")
                self.__configRaw = Config({}).to_dict()
                self.__save_config()
                self.__logger.error("Check your config and try again.")
                exit()
            except json.decoder.JSONDecodeError as e1:
                self.__logger.error("Can't load config.json: JSON decode error:{0}".format(str(e1.args)))
                self.__logger.error("Check your config format and try again.")
                exit()
        self.__config = Config(self.__configRaw)
        self.__configRaw = self.__config.to_dict()
        self.__save_config()

    def get_config(self) -> Config:
        return self.__config

    def __save_config(self):
        with open('./config.json', 'w') as fs:
            json.dump(self.__configRaw, fs, indent=2)
