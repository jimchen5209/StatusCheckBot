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

import psutil
import os
import json
from pathlib import Path

path = str(Path.home()) + '/.bot_status'

if not os.path.isdir(path):
    os.mkdir(path)


def get_status():
    status = {}

    for walk in os.walk(path):
        for file in walk[2]:
            with open(path + '/' + file, 'r') as fs:
                bot_status = json.loads(fs.read())
            try:
                p = psutil.Process(bot_status['pid'])
                if p.cmdline()[1] == bot_status['cmdline'][0] and p.name().startswith('python'):
                    status[bot_status['name']] = {'online': True}
            except psutil.NoSuchProcess:
                status[bot_status['name']] = {'online': False}

    return status
