# import base64
# import json
import os
# import urllib
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ChatType
# from datetime import datetime
# import numpy as np
# from PIL import Image
# import requests
# from json import JSONEncoder
# from io import BytesIO

from utils.cmc import OREPrice
from utils.eos import get_info, get_balance, create_new_keypair
from utils.logger import logger as Logger
from utils.redis import Redis
# from utils.pinata import Pinata

logger = Logger
latest_price = OREPrice()
redis = Redis()
storage = MemoryStorage()
# pinata = Pinata()

bot = Bot(
    token=os.getenv('TELEGRAM_BOT_API_KEY'),
    parse_mode=types.ParseMode.HTML
)


class AdminFilter(BoundFilter):
    key: str = 'is_admin'

    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def check(self, message: types.Message):
        member = await bot.get_chat_member(
            message.chat.id, message.from_user.id
        )
        return member.is_chat_admin()


class Help(StatesGroup):
    active = State()


class Photo(StatesGroup):
    exists = State()


dp = Dispatcher(bot, storage=storage)
dp.filters_factory.bind(AdminFilter)


@dp.message_handler(commands=['info', 'links'])
async def start_cmd_handler(message: types.Message):
    keyboard_markup = types.ReplyKeyboardMarkup(row_width=3)
    # default row_width is 3, so here we can omit it actually
    # kept for clearness

    btns_text = ('🕸 ORE NETWORK', '👨‍⚕️ ORE-ID', '🏦 ORE VAULT')
    keyboard_markup.row(
        *(types.KeyboardButton(text) for text in btns_text)
    )
    # adds buttons as a new row to the existing keyboard
    # the behaviour doesn't depend on row_width attribute

    more_btns_text = (
        "📑 White Paper",
        "🛣 Road Map",
        "🧑‍💻 GitHub",
        "⛓ Block Explorer",
        "👨‍👧‍👧 Team",
        "🧙‍♂️ API"
    )
    keyboard_markup.add(
        *(types.KeyboardButton(text) for text in more_btns_text)
    )
    # adds buttons. New rows are formed according to row_width parameter

    await Help.active.set()

    await message.reply("How can I help?", reply_markup=keyboard_markup)


@dp.message_handler(state=Help.active)
async def help_msg_handler(message: types.Message, state: FSMContext):
    # pressing of a KeyboardButton is the same as sending the regular message
    # with the same text so, to handle the responses from the keyboard, we
    # need to use a message_handler in real bot, it's better to define
    # message_handler(text="...") for each button but here for the
    # simplicity only one handler is defined

    button_text = message.text
    logger.debug('The answer is %r', button_text)  # print the text we've got

    match button_text:
        case '🕸 ORE NETWORK':
            reply_text = "<a href='https://ore.network/'>https://ore.network/</a>"
        case '👨‍⚕️ ORE-ID':
            reply_text = "<a href='https://oreid.io/'>https://oreid.io/</a>"
        case '🏦 ORE VAULT':
            reply_text = "<a href='https://oreid.io/'>https://oreid.io/</a>"
        case '📑 White Paper':
            reply_text = "<a href='https://ore.network/wp-content/uploads/2021/09/ORE-Whitepaper-2.0.pdf'>ORE-Whitepaper-2.0.pdf</a>"
        case '🛣 Road Map':
            reply_text = "<a href='https://oreid.io/'>https://oreid.io/</a>"
        case '🧑‍💻 GitHub':
            reply_text = "<a href='https://github.com/Open-Rights-Exchange'>https://github.com/Open-Rights-Exchange</a>"
        case '⛓ Block Explorer':
            reply_text = "<a href='https://explorer.ore.network/'>https://explorer.ore.network/</a>"
        case '👨‍👧‍👧 Team':
            reply_text = "<a href='https://oreid.io/'>https://oreid.io/</a>"
        case '🧙‍♂️ API':
            reply_text = "<a href='https://oreid.io/'>https://oreid.io/</a>"
        case _:
            reply_text = "Not a valid response!"

    await message.reply(reply_text, reply_markup=types.ReplyKeyboardRemove())
    # with message, we send types.ReplyKeyboardRemove() to hide the keyboard

    # Reset the State
    logger.debug(await state.reset_state())
    # await state.finish()


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
    await bot.send_message(
        message.chat.id,
        f'ORE Price: ${latest_price.price}\n'
        f'Percent Change (24h): {latest_price.price_change_24h}%'
    )


@dp.message_handler(commands=['volume', 'v'])
async def get_volume(message: types.Message):
    """
    This handler will return the current ORE 24Hr Volume
    """
    await latest_price.update_price()
    await bot.send_message(
        message.chat.id,
        f'ORE Volume (24h): ${latest_price.volume_24h:,}'
    )


@dp.message_handler(commands=['test'])
async def test(message: types.Message):
    """
    This handler will be called when user sends `/test` command
    """
    # Testing functions:
    get_balance(os.getenv('TEST_USER_OREID'))
    create_new_keypair()


@dp.message_handler(commands=['block', 'b'])
async def block_chain_info(message: types.Message):
    """
    This handler will be called when user send '/block' command
    """
    ore_block_info = get_info()
    head_block = ore_block_info['head_block_num']
    block_producer = ore_block_info['head_block_producer']
    await bot.send_message(
        message.chat.id,
        f'ORE Head Block: {head_block:,}\n'
        f'Current Block Producer: {block_producer}'
    )


@dp.message_handler(commands=['tip', 't'], is_admin=True)
async def tip_user(message: types.Message):
    """
    This handler sends ORE Tokens to another user
    """
    msg_sender = message.from_user.id
    logger.debug(f'msg_sender: {msg_sender}')

    full_command = message.get_full_command()
    logger.debug(f'full_command: {full_command}')

    # seperate the command from the args
    try:
        (command, recipient_and_amount) = full_command
        (recipient, amount) = str(recipient_and_amount).split()
        is_command = True
    except Exception as exc:
        await message.reply(
            'Not a Command. Please try again. Ex: "/tip @recipient 11.0"'
        )
        is_command = False
        logger.error(exc)

    # Check if the command is /tip
    if command != '/tip':
        logger.error(f'Something went wrong! {command} is not "/tip"')
    elif is_command:
        logger.debug(f'recipient: {recipient}')

        tip_amount = amount
        logger.debug(f'tip_amount: {tip_amount}')

        try:
            await message.reply(
                f'✅ Successfully Tipped {recipient} {tip_amount} ORE 🎉'
            )
        except Exception as exc:
            logger.error(exc)
            logger.error('/Tip did not complete sucessfully')

        # msg_as_json = message.as_json
        # logger.debug(msg_as_json)


@dp.message_handler(commands=['submit'], state="*")
async def start_submit(message: types.Message):
    logger.debug(
        'submission process started'
    )
    await Photo.exists.set()
    await message.reply(f'{message.from_user.mention} Please upload your JPG photo')


@dp.message_handler(content_types=["photo", "file"], state=Photo.exists)
async def download_photo(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    logger.debug(f'user_id: {user_id}')
    path = 'meme_entries'
    image = f'image-{user_id}.jpg'
    # Check for previous entry

    # dir_list = os.listdir('./meme_entries')
    # logger.debug(dir_list)
    # for img in dir_list:
    if os.path.exists(f'{path}/{image}'):
        await message.reply("You already have submitted your entry. You can use /delete_meme to remove your current entry and upload a new one.")
        await state.reset_state()
        # https://giters.com/aiogram/aiogram/issues/665
        return
    else:
        try:
            await message.photo[-1].download(destination_file=f'./{path}/{image}', make_dirs=True)
            await message.reply(f'{message.from_user.mention} Your entry has been accepted!')
        except Exception as exc:
            await message.reply(f"Sorry, your entry was not submitted! {exc}")

    await state.reset_state()


@dp.message_handler(commands=["delete_meme"])
async def del_photo(message: types.Message):
    user_id = message.from_user.id
    logger.debug(f'user_id: {user_id}')
    path = './meme_entries'
    image = f'image-{user_id}.jpg'
    try:
        if os.path.exists(f'{path}/{image}'):
            os.remove(f'{path}/{image}')
            await message.reply(f'{message.from_user.mention} Your entry has been deleted')
        else:
            await message.reply(f'{message.from_user.mention} You have no entry for the Meme Contest. Type /submit to get started')
    except Exception as exc:
        await message.reply(f'{message.from_user.mention} Entry Deletion failed. {exc}')


@dp.message_handler(commands=["entry"])
async def get_photo(message: types.Message):
    user_id = message.from_user.id
    # logger.debug(f'user_id: {user_id}')
    path = 'meme_entries'
    image = f'image-{user_id}.jpg'
    try:
        with open(f'{path}/{image}', "r+b") as photo:
            await message.reply_photo(photo, caption=f"Meme Entry by {message.from_user.mention}")
        # await message.reply_photo(os.open(image, 'rb'))
    except Exception as exc:
        await message.reply(f'{message.from_user.mention} Entry View failed. {exc}')


# @dp.message_handler(commands=["hits"])
# async def get_hits(message: types.Message):
#     hits = await redis.get_value(f'{str(message.from_user.id)}_hits')
#     await message.reply(f'{message.from_user.mention} has {hits} hits.')


# @dp.message_handler(chat_type=ChatType.SUPERGROUP)
# async def add_hit(message: types.Message):
#     user_hit = f'{str(message.from_user.id)}_hits'
#     logger.debug(f'user_hit: {user_hit}')
#     redis_return = await redis.inc_value(user_hit)
#     logger.debug(f'redis_return for redis.inc_value: {redis_return}')

#     if not message.from_user.is_bot:
#         total_return = await redis.inc_value('Total_Hits')
#         logger.debug(f'total_return for redis.inc_value: {total_return}')

if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=False)
