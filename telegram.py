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
import asyncio
import logging
from enum import Enum

from aiogram import Bot, Dispatcher, executor, types

from app import Main


class ServerStatus(Enum):
    online = "✅ {name} is up"
    offline = "❌ {name} is down"
    unknown = "❔ {name} returned a unknown status"
    new_online = "🆕✅ {name} just popped up and indicates online"
    new_offline = "🆕❌ {name} showed up but it is offline"
    deleted = "🗑 {name} has been deleted"
    node_down = "🚫 Errored when fetching status from node `{ip}`: {message}"


class Telegram:
    def __init__(self, main: Main):
        self.__logger = logging.getLogger("Telegram")
        logging.basicConfig(level=logging.INFO)
        self.__logger.info("Loading Telegram...")
        self.__main = main
        self.__config = main.config
        self.bot = Bot(token=self.__config.telegram_token)
        self.dispatcher = Dispatcher(self.bot)
        self.loop = asyncio.get_event_loop()

        @self.dispatcher.message_handler(commands=['start'])
        async def start(message: types.Message):
            await message.reply("Hi")

    def send_status_message(self, message: str):
        execute = asyncio.run_coroutine_threadsafe(self.bot.send_message(
            self.__config.telegram_admin,
            message,
            parse_mode="Markdown"
        ), self.loop)
        execute.result()

    def start(self):
        executor.start_polling(self.dispatcher, skip_updates=True)
