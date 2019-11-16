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

import json
import logging
import os
from pathlib import Path

import psutil
import requests


class Status:
    __path = str(Path.home()) + '/.bot_status'
    data = {}

    def __init__(self):
        self.__logger = logging.getLogger("Status")
        logging.basicConfig(level=logging.INFO)
        if not os.path.isdir(self.__path):
            os.mkdir(self.__path)
        self.nodes = []
        self.__main_server = True
        self.update_status()

    def set_node_mode(self):
        self.__main_server = False

    def update_nodes(self, nodes: list):
        self.nodes = nodes
        self.update_status()

    def get_status(self) -> dict:
        if not self.__main_server:
            self.update_status()
        return self.data

    def update_status(self):
        self.data.clear()
        for walk in os.walk(self.__path):
            for file in walk[2]:
                with open(self.__path + '/' + file, 'r') as fs:
                    bot_status = json.loads(fs.read())
                try:
                    p = psutil.Process(bot_status['pid'])
                    if p.cmdline()[1] == bot_status['cmdline'][0] and p.name().startswith('python'):
                        self.data[bot_status['name']] = {'online': True}
                except psutil.NoSuchProcess:
                    self.data[bot_status['name']] = {'online': False}
        if len(self.nodes) != 0:
            self.__update_node()

    def __update_node(self):
        for url in self.nodes:
            self.__logger.info("Syncing from {url}...".format(url=url))
            try:
                r = requests.get("{base_url}/getStatus/refreshNow".format(base_url=url))
            except requests.exceptions.ConnectionError as e1:
                self.__logger.error(str(e1.args))
                continue
            else:
                if r.status_code == requests.codes.ok:
                    self.__merge_content(json.loads(r.text))
                else:
                    self.__logger.error("Server returned {code} : {msg}".format(code=str(r.status_code), msg=str(r.reason)))

    def __merge_content(self, new_data: dict):
        for i in new_data:
            if i not in self.data:
                self.data[i] = new_data[i]
            else:
                self.__logger.warning(
                    "{name} exists on both server side, trying to merge, consider deleting one of them".format(name=i))
                if not self.data[i] and new_data[i]:
                    self.data[i] = True
                elif self.data[i] and not new_data[i]:
                    pass
                elif self.data[i] and new_data[i]:
                    self.__logger.warning(
                        "{name} are both online!!! Consider closing or rename one of them".format(name=i))
                else:
                    pass
