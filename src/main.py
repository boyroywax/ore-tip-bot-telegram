import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import BoundFilter

from utils.cmc import OREPrice
from utils.eos import get_info, get_balance, create_new_keypair
from utils.logger import logger as Logger

latest_price = OREPrice()
logger = Logger

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
    # pressing of a KeyboardButton is the same as sending the regular message with the same text
    # so, to handle the responses from the keyboard, we need to use a message_handler
    # in real bot, it's better to define message_handler(text="...") for each button
    # but here for the simplicity only one handler is defined

    button_text = message.text
    logger.debug('The answer is %r', button_text)  # print the text we've got

    if button_text == 'Yes!':
        reply_text = "That's great"
    elif button_text == 'No!':
        reply_text = "Oh no! Why?"
    else:
        reply_text = "Keep calm...Everything is fine"

    await message.reply(reply_text, reply_markup=types.ReplyKeyboardRemove())
    # with message, we send types.ReplyKeyboardRemove() to hide the keyboard
    # await bot.send_message(message.chat.id, "Hi!\nI'm The ORE Tip Bot!\nPowered by the ORE Network")


@dp.message_handler(commands=['admin', 'a'], is_admin=True)
async def admin_panel(message: types.Message):
    """
    This handler is an admin panel launched by '/admin' command
    """    
    await bot.send_message(message.chat.id, "Welcome to the Admin Panel")

@dp.message_handler(commands=['price', 'p'])
async def get_price(message: types.Message):
    """
    This handler will return the current ORE price and 24h price percent change
    """
    await latest_price.update_price()
    await bot.send_message(message.chat.id, f'ORE Price: ${latest_price.price}\nPercent Change (24h): {latest_price.price_change_24h}%')

@dp.message_handler(commands=['volume', 'v'])
async def get_volume(message: types.Message):
    """
    This handler will return the current ORE 24Hr Volume
    """
    await latest_price.update_price()
    await bot.send_message(message.chat.id, f'ORE Volume (24h): ${latest_price.volume_24h:,}')

@dp.message_handler(commands=['test', 't'], state="*")
async def test(message: types.Message):
    """
    This handler will be called when user sends `/test` command
    """
    # Testing functions:
    get_balance('ore1shlejxsp')
    create_new_keypair()

@dp.message_handler(commands=['block', 'b'], state="*")
async def block_chain_info(message: types.Message):
    """
    This handler will be called when user send '/block' command
    """
    ore_block_info = get_info()
    head_block = ore_block_info['head_block_num']
    block_producer = ore_block_info['head_block_producer']
    await bot.send_message(message.chat.id, f'ORE Head Block: {head_block:,}\nCurrent Block Producer: {block_producer:}')

if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)
