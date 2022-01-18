import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import BoundFilter

from utils.cmc import OREPrice
from utils.eos import get_info, get_balance, create_new_keypair

latest_price = OREPrice()

bot = Bot(token=os.getenv('TELEGRAM_BOT_API_KEY'),  parse_mode=types.ParseMode.HTML)

class AdminFilter(BoundFilter):
    key: str = 'is_admin'

    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def check(self, message: types.Message):
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.is_chat_admin()

dp = Dispatcher(bot)
dp.filters_factory.bind(AdminFilter)

@dp.message_handler(commands=['start', 'help'], state="*")
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await bot.send_message(message.chat.id, "Hi!\nI'm The ORE Tip Bot!\nPowered by the ORE Network")


@dp.message_handler(commands=['admin'], is_admin=True)
async def admin_panel(message: types.Message):
    """
    This handler is an admin panel launched by '/admin' command
    """    
    await bot.send_message(message.chat.id, "Welcome to the Admin Panel")

@dp.message_handler(commands=['price'])
async def get_price(message: types.Message):
    """
    This handler will return the current ORE price and 24h price percent change
    """
    await latest_price.update_price()
    await bot.send_message(message.chat.id, f'ORE Price: ${latest_price.price}\nPercent Change (24h): {latest_price.price_change_24h}%')

@dp.message_handler(commands=['volume'])
async def get_volume(message: types.Message):
    """
    This handler will return the current ORE 24Hr Volume
    """
    await latest_price.update_price()
    await bot.send_message(message.chat.id, f'ORE Volume (24h): ${latest_price.volume_24h}')

@dp.message_handler(commands=['test'], state="*")
async def test(message: types.Message):
    """
    This handler will be called when user sends `/test` command
    """
    # Testing functions:
    get_info()
    get_balance('ore1shlejxsp')
    create_new_keypair()

if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)
