from logging import Logger

import os
from aiogram import Bot, Dispatcher, executor, types
from utils.logger import logger as Loggger

logger = Logger

bot = Bot(token=os.getenv('TELEGRAM_BOT_API_KEY'))
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)