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

from app import Main
from telegram import ServerStatus


class Status:
    __path = str(Path.home()) + '/.bot_status'
    data = {}
    __last_error={}

    def __init__(self, main: Main):
        self.__logger = logging.getLogger("Status")
        logging.basicConfig(level=logging.INFO)
        if not os.path.isdir(self.__path):
            os.mkdir(self.__path)
        self.__nodes = []
        self.__telegram = main.telegram
        self.__main_server = True
        self.update_status(True)

    def set_node_mode(self):
        self.__main_server = False

    def update_nodes(self, nodes: list, disable_telegram: bool = False):
        self.__nodes = nodes
        self.update_status(disable_telegram)

    def get_status(self) -> dict:
        if not self.__main_server:
            self.update_status()
        return self.data

    def update_status(self, disable_telegram: bool = False) -> dict:
        old = self.data.copy()
        self.__update_status()
        new = self.data.copy()
        updated = {}
        for i in new:
            if i not in old:
                updated[i] = new[i].copy()
                updated[i]['update_type'] = 'new'
            else:
                if new[i] != old[i]:
                    updated[i] = new[i].copy()
                    updated[i]['update_type'] = 'updated'
        for i in old:
            if i not in new:
                updated[i] = old[i].copy()
                updated[i]['update_type'] = 'removed'
        if len(updated) != 0:
            self.__logger.info("Updated: {0}".format(str(updated)))
            if self.__telegram and (not disable_telegram):
                for stat in updated:
                    current = updated[stat]
                    if current['update_type'] == 'updated':
                        self.__telegram.send_status_message(
                            (ServerStatus.online.value if current['online'] else ServerStatus.offline.value).format(
                                name=stat
                            )
                        )
                    elif current['update_type'] == 'new':
                        self.__telegram.send_status_message(
                            (
                                ServerStatus.new_online.value
                                if current['online'] else
                                ServerStatus.new_offline.value
                            ).format(
                                name=stat
                            )
                        )
                    elif current['update_type'] == 'removed':
                        self.__telegram.send_status_message(ServerStatus.deleted.value.format(name=stat))
                    else:
                        self.__telegram.send_status_message(ServerStatus.unknown.value.format(name=stat))
        return updated

    def __update_status(self):
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
        if len(self.__nodes) != 0:
            self.__update_node()

    def __update_node(self):
        for url in self.__nodes:
            self.__logger.info("Syncing from {url}...".format(url=url))
            try:
                r = requests.get("{base_url}/getStatus/refreshNow".format(base_url=url))
            except requests.exceptions.ConnectionError as e1:
                self.__logger.error(str(e1.args))
                if url in self.__last_error:
                    if e1 == self.__last_error[url]:
                        continue
                self.__last_error[url] = e1
                if self.__telegram:
                    self.__telegram.send_status_message(ServerStatus.node_down.value.format(
                        ip=url,
                        message=str(e1.args)
                    ))
                continue
            else:
                if r.status_code == requests.codes.ok:
                    self.__merge_content(json.loads(r.text))
                else:
                    self.__logger.error(
                        "Server returned {code} : {msg}".format(code=str(r.status_code), msg=str(r.reason)))
                    if self.__telegram:
                        self.__telegram.send_status_message(ServerStatus.node_down.value.format(
                            ip=url,
                            message="{code} : {msg}".format(code=str(r.status_code), msg=str(r.reason))
                        ))

    def __merge_content(self, new_data: dict):
        for i in new_data:
            if i not in self.data:
                self.data[i] = new_data[i]
            else:
                self.__logger.warning(
                    "{name} exists on both server side, trying to merge, consider deleting one of them".format(name=i))
                if not self.data[i]['online'] and new_data[i]['online']:
                    self.data[i]['online'] = True
                elif self.data[i]['online'] and not new_data[i]['online']:
                    pass
                elif self.data[i]['online'] and new_data[i]['online']:
                    self.__logger.warning(
                        "{name} are both online!!! Consider closing or rename one of them".format(name=i))
                    self.data[i]['online'] = True
                else:
                    pass
