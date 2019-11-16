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

# !/usr/bin/env python

from __future__ import print_function

import logging
import os
import time


class Logger:
    __logPath = "./logs/{0}".format(time.strftime("%Y-%m-%d-%H-%M-%S"))

    def __init__(self):
        if not os.path.isdir("./logs"):
            os.mkdir("./logs")
        self.__log_format = "[%(asctime)s][%(threadName)s/%(name)s]%(levelname)s %(message)s"
        logging.root.name = "Main"
        logging.root.setLevel(logging.INFO)

        self.logger = logging.getLogger()
        self.__handler = logging.FileHandler(
            filename="{0}.log".format(self.__logPath),
            encoding="utf-8",
            mode="w"
        )
        self.__handler.level = logging.INFO
        self.__handler.setFormatter(logging.Formatter(self.__log_format))
        self.logger.addHandler(self.__handler)
