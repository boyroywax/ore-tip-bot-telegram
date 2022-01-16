import os
from aiogram.dispatcher.filters import BoundFilter
from aiogram import Bot, Dispatcher, executor, types
from utils.cmc import CMC, OREPrice
from datetime import datetime

from utils.eos import get_info, get_balance, create_new_keypair

class MyFilter(BoundFilter):
    key: str = 'is_admin'

    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def check(self, message: types.Message):
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.is_chat_admin()

cmc = CMC()
latest_price = OREPrice()
latest_price.set_datetime(datetime.now())

bot = Bot(token=os.getenv('TELEGRAM_BOT_API_KEY'),  parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
dp.filters_factory.bind(MyFilter)

@dp.message_handler(commands=['start', 'help'], state="*")
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    # Testing functions:
    get_info()
    get_balance('ore1shlejxsp')
    create_new_keypair()

    await bot.send_message(message.chat.id, "Hi!\nI'm The ORE Tip Bot!\nPowered by the ORE Network")

# @dp.message_handler(content_types=types.ContentTypes.ANY)
# async def echo(message: types.Message):
#     await bot.send_message(message.chat.id, message.text)

@dp.message_handler(commands=['admin'], is_admin=True)
async def admin_panel(message: types.Message):
    """
    This handler is an admin panel launched by '/admin' command
    """    
    await bot.send_message(message.chat.id, "Welcome to the Admin Panel")

@dp.message_handler(commands=['price'])
async def get_price(message: types.Message):
    """
    This handler will return the current ORE price
    """
    time_diff = datetime.now() - latest_price.datetime
    if latest_price.price == 0.0:
        await latest_price.update_price()
    elif time_diff.total_seconds() >= 60:
        await latest_price.update_price()

    # logger.debug(f'ore price: ${ore_price}')
    await bot.send_message(message.chat.id, f'ORE Price: ${latest_price.price}')


if __name__ == '__main__':
    executor.start_polling(dispatcher = dp, skip_updates=True)
