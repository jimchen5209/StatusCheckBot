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


class Main:
    def __init__(self):
        from logger import Logger
        from config import ConfigManager
        from server import StatusServer
        from telegram import Telegram
        from status import Status
        self.logger = Logger()
        self.logger.logger.info("Starting...")

        self.config = ConfigManager().get_config()

        if self.config.telegram_token:
            self.telegram = Telegram(self)
            if self.telegram:
                from threading import Thread
                Thread(target=self.telegram.start, name="TelegramBot").start()
        else:
            self.telegram = None

        self.status = Status(self)

        self.server = StatusServer(self)
        self.server.start_server()


if __name__ == '__main__':
    main = Main()
