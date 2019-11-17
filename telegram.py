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
import json
import logging
import time
from enum import Enum

from aiogram import Bot, Dispatcher, executor, types

from app import Main


class ServerStatus(Enum):
    online = "✅ {name} is up"
    online_list = "✅ {name} is online"
    online_sub = "✅ {name} is currently online"
    offline = "❌ {name} is down"
    offline_list = "❌ {name} is offline"
    offline_sub = "❌ {name} is currently offline"
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
            await message.reply("Jim's Bot Status")

        @self.dispatcher.message_handler(commands=['status'])
        async def get_status(message: types.Message):
            status = self.__main.status.get_status()
            msg = self.__status_to_string(status)
            refresh_button = types.inline_keyboard.InlineKeyboardButton(
                text="🔄 Refresh Now",
                callback_data=json.dumps({'t': 'refresh', 'o': message.from_user.id})
            )
            markup = types.inline_keyboard.InlineKeyboardMarkup().add(refresh_button)
            await message.reply(msg, reply_markup=markup)

        @self.dispatcher.callback_query_handler()
        async def on_callback_query(callback_query: types.CallbackQuery):
            data = json.loads(callback_query.data)
            if 't' not in data or 'o' not in data:
                await callback_query.answer("Invalid Button!")
                await callback_query.message.edit_reply_markup(None)
                return
            if data['t'] == 'refresh':
                if data['o'] != callback_query.message.reply_to_message.from_user.id:
                    await callback_query.answer("This button is not yours!!", show_alert=True)
                    return
                refreshing = types.inline_keyboard.InlineKeyboardButton(
                    text="🔄 Refreshing...",
                    callback_data=json.dumps({'t': 'none', 'o': data['o']})
                )
                markup = types.inline_keyboard.InlineKeyboardMarkup().add(refreshing)
                await callback_query.message.edit_reply_markup(markup)
                self.__main.status.update_status(True)
                status = self.__main.status.get_status()
                msg = self.__status_to_string(status)
                msg += '\nUpdated: {time}'.format(time=time.strftime("%Y/%m/%d %H:%M:%S"))
                if callback_query.message.text != msg:
                    await callback_query.message.edit_text(msg, reply_markup=callback_query.message.reply_markup)
                await callback_query.answer("Updated!")

    def send_status_message(self, message: str):
        execute = asyncio.run_coroutine_threadsafe(self.bot.send_message(
            self.__config.telegram_admin,
            message,
            parse_mode="Markdown"
        ), self.loop)
        execute.result()

    @staticmethod
    def __status_to_string(status: dict) -> str:
        msg = ""
        for name in status:
            if status[name]['online']:
                msg += ServerStatus.online_list.value.format(name=name) + '\n'
            else:
                msg += ServerStatus.offline_list.value.format(name=name) + '\n'
        return msg

    def start(self):
        executor.start_polling(self.dispatcher, skip_updates=True)
