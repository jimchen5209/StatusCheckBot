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
    data_with_server = {}
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

    def get_detailed_status(self) -> dict:
        if not self.__main_server:
            self.update_status()
        return self.data_with_server

    def get_down_server(self) -> dict:
        return self.__last_error

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
                output = ""
                for stat in updated:
                    current = updated[stat]
                    if current['update_type'] == 'updated':
                        output += (ServerStatus.online.value if current['online'] else ServerStatus.offline.value).format(name=stat)
                    elif current['update_type'] == 'new':
                        output += (ServerStatus.new_online.value if current['online'] else ServerStatus.new_offline.value).format(name=stat)
                    elif current['update_type'] == 'removed':
                        output += ServerStatus.deleted.value.format(name=stat)
                    else:
                        output += ServerStatus.unknown.value.format(name=stat)
                    output += '\n'
                self.__telegram.send_status_message(output)
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
                        self.__set_data(bot_status['name'], True, 'python', 'local')
                        continue
                    if p.name().startswith('node'):
                        if 'pm2' in bot_status and bot_status['pm2']:
                            if p.cmdline()[0].split(' ')[1] == bot_status['cmdline'][1]:
                                self.__set_data(bot_status['name'], True, 'node-pm2', 'local')
                                continue
                        elif p.cmdline()[1] == bot_status['cmdline'][1]:
                            self.__set_data(bot_status['name'], True, 'node', 'local')
                            continue
                    self.__set_data(bot_status['name'], False, server='local')
                except psutil.NoSuchProcess:
                    self.__set_data(bot_status['name'], False, server='local')
        if len(self.__nodes) != 0:
            self.__update_node()

    def __set_data(self,name: str, online: bool, type: str = 'none', server: str = 'none'):
        self.data[name] = {'online': online, 'type': type}
        self.data_with_server[name] = {'online': online, 'type': type, 'server': server}

    def __update_node(self):
        for url in self.__nodes:
            self.__logger.info("Syncing from {url}...".format(url=url))
            try:
                r = requests.get("{base_url}/getStatus/refreshNow".format(base_url=url))
            except requests.exceptions.ConnectionError as e1:
                self.__logger.error(str(e1.args))
                if url in self.__last_error:
                    if self.__last_error[url] == "ConnectionError":
                        continue
                self.__last_error[url] = "ConnectionError"
                if self.__telegram:
                    self.__telegram.send_status_message(ServerStatus.node_down.value.format(
                        ip=url,
                        message=str(e1.args)
                    ))
                continue
            else:
                if r.status_code == requests.codes.ok:
                    if url in self.__last_error:
                        del self.__last_error[url]
                    self.__merge_content(json.loads(r.text), url)
                else:
                    self.__logger.error(
                        "Server returned {code} : {msg}".format(code=str(r.status_code), msg=str(r.reason)))
                    if url in self.__last_error:
                        if self.__last_error[url] == "HTTPError":
                            continue
                    self.__last_error[url] = "HTTPError"
                    if self.__telegram:
                        self.__telegram.send_status_message(ServerStatus.node_down.value.format(
                            ip=url,
                            message="{code} : {msg}".format(code=str(r.status_code), msg=str(r.reason))
                        ))

    def __merge_content(self, new_data: dict, server: str):
        for i in new_data:
            if i not in self.data:
                self.data[i] = new_data[i]
                self.data[i]['type'] = new_data[i]['type'] if 'type' in new_data[i] else 'python'
            else:
                self.__logger.warning(
                    "{name} exists on both server side, trying to merge, consider deleting one of them".format(name=i))
                if not self.data[i]['online'] and new_data[i]['online']:
                    self.data[i]['online'] = True
                    self.data[i]['type'] = new_data[i]['type'] if 'type' in new_data[i] else 'python'
                elif self.data[i]['online'] and not new_data[i]['online']:
                    pass
                elif self.data[i]['online'] and new_data[i]['online']:
                    self.__logger.warning("{name} are both online!!! Consider closing or rename one of them".format(name=i))
                    self.data[i]['online'] = True
                    self.data[i]['type'] = new_data[i]['type'] if 'type' in new_data[i] else 'python'
                else:
                    pass
            self.__set_data(i, self.data[i]['online'], self.data[i]['type'], server if new_data[i]['online'] else ('local' if self.data[i]['online'] else 'none'))
