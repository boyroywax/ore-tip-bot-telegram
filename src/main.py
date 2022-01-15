import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import BoundFilter

from utils.eos import get_info, get_balance
from utils.logger import logger as Logger


class MyFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def check(self, message: types.Message):
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.is_chat_admin()

logger = Logger

bot = Bot(token=os.getenv('TELEGRAM_BOT_API_KEY'),  parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
dp.filters_factory.bind(MyFilter)


@dp.message_handler(commands=['start', 'help'], state="*")
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    get_info()
    get_balance('ore1shlejxsp')
    await bot.send_message(message.chat.id, "Hi!\nI'm The ORE Tip Bot!\nPowered by the ORE Network")

# @dp.message_handler(content_types=types.ContentTypes.ANY)
# async def echo(message: types.Message):
#     await bot.send_message(message.chat.id, message.text)

@dp.message_handler(commands=['admin'], is_admin=True)
async def admin_panel(message: types.Message):
    """
    This handler is an admin panel launched by '/admin' command
    """
    # await message.reply("Welcome to the Admin Portal!")
    
    await bot.send_message(message.chat.id, "Welcome to the Admin Panel")

if __name__ == '__main__':
    executor.start_polling(dispatcher = dp, skip_updates=True)
