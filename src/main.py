import csv
import json
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ChatType

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


async def get_command(message: types.Message):
    full_command = message.get_full_command()
    logger.debug(f'full_command: {full_command}')

    # seperate the command from the args
    try:
        (command, recipient_and_amount) = full_command
        (recipient, amount) = str(recipient_and_amount).split()
        return(command, recipient, amount)
    except Exception as exc:
        logger.error(exc)
        (command, recipient) = full_command
        return(command, recipient)
        # await message.reply(
        #     'Not a Command. Please try again. Ex: "/tip @recipient 11.0"'
        # )
        # return (None, None, None)


async def get_mentioned_user(user_mention: int):
    try:
        user_name = await redis.get_value(user_mention)
        return user_name
    except Exception as exc:
        logger.debug(f'get_mentioned failed: {exc}')

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
    # await bot.send_message(message.chat.id, "Clearing Redis...")
    # await redis.flush_all()
    # await bot.send_message(message.chat.id, "Redis Cache cleared!")


@dp.message_handler(commands=['test'], is_admin=True)
async def test(message: types.Message):
    """
    This handler will be called when user sends `/test` command
    """
    # Testing functions:
    get_balance(os.getenv('TEST_USER_OREID'))
    create_new_keypair()


@dp.message_handler(commands=['get_entries'], is_admin=True)
async def get_entries(message: types.Message):
    """
    This handler is an admin panel launched by '/admin' command
    """
    await bot.send_message(message.chat.id, "Fetching All The Entries")
    entries = os.listdir('./meme_entries')
    for image in entries:
        if image == 'test':
            pass
        else:
            logger.debug(f'Entry: {image}')
            user_id, file_ext = image.split('.')
            with open(f'./meme_entries/{image}', "r+b") as photo:
                try:
                    user = await bot.get_chat_member(chat_id=message.chat.id, user_id=user_id[6:])
                    await message.reply_photo(photo, caption=f"Meme Entry by {user.user.mention}")
                except Exception:
                    user = 'Not Found'
                    await message.reply_photo(photo, caption=f"Meme Entry by {user_id[6:]}")


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

    (command, recipient, amount) = await get_command(message)

    # Check if the command is /tip
    if command != '/tip':
        logger.error(f'Something went wrong! {command} is not "/tip"')
    else:
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


# @dp.message_handler(commands=['submit'], state="*")
# async def start_submit(message: types.Message):
#     # pair the user_name with user_id
#     await redis.set_value(message.from_user.mention, str(message.from_user.id))

#     logger.debug(
#         'submission process started'
#     )
#     await redis.set_value(message.from_user.mention, str(message.from_user.id))
#     await Photo.exists.set()
#     await message.reply(f'{message.from_user.mention} Please upload your JPG photo')


# @dp.message_handler(content_types=["photo", "file"], state=Photo.exists)
# async def download_photo(message: types.Message, state: FSMContext):
#     # pair the user_name with user_id
#     await redis.set_value(message.from_user.mention, str(message.from_user.id))

#     user_id = message.from_user.id
#     logger.debug(f'user_id: {user_id}')
#     path = 'meme_entries'
#     image = f'image-{user_id}.jpg'

#     if os.path.exists(f'{path}/{image}'):
#         await message.reply("You already have submitted your entry. You can use /delete_meme to remove your current entry and upload a new one.")
#         await state.reset_state()
#         # https://giters.com/aiogram/aiogram/issues/665
#         return
#     else:
#         try:
#             await message.photo[-1].download(destination_file=f'./{path}/{image}', make_dirs=True)
#             await message.reply(f'{message.from_user.mention} Your entry has been accepted!')
#         except Exception as exc:
#             await message.reply(f"Sorry, your entry was not submitted! {exc}")

#     await state.reset_state()


# @dp.message_handler(commands=["delete_meme"])
# async def del_photo(message: types.Message):
#     # pair the user_name with user_id
#     await redis.set_value(message.from_user.mention, str(message.from_user.id))

#     user_id = message.from_user.id
#     logger.debug(f'user_id: {user_id}')
#     path = './meme_entries'
#     image = f'image-{user_id}.jpg'
#     try:
#         if os.path.exists(f'{path}/{image}'):
#             os.remove(f'{path}/{image}')
#             await message.reply(f'{message.from_user.mention} Your entry has been deleted')
#         else:
#             await message.reply(f'{message.from_user.mention} You have no entry for the Meme Contest. Type /submit to get started')
#     except Exception as exc:
#         await message.reply(f'{message.from_user.mention} Entry Deletion failed. {exc}')


@dp.message_handler(commands=["entry"])
async def get_photo(message: types.Message):
    # pair the user_name with user_id
    await redis.set_value(message.from_user.mention, str(message.from_user.id))

    user_id = message.from_user.id
    # logger.debug(f'user_id: {user_id}')
    path = 'meme_entries'
    image = f'image-{user_id}.jpg'
    try:
        if os.path.exists(f'./{path}/{image}'):
            with open(f'{path}/{image}', "r+b") as photo:
                await message.reply_photo(photo, caption=f"Meme Entry by {message.from_user.mention}")
            # await message.reply_photo(os.open(image, 'rb'))
        else:
            await message.reply(f'{message.from_user.mention}, you have no entry for the Meme Contest. Type /submit to get started')
    except Exception as exc:
        await message.reply(f'{message.from_user.mention} Entry View failed. {exc}')


@dp.message_handler(commands=["check"])
async def check_photo(message: types.Message):
    # pair the user_name with user_id
    # await redis.set_value(message.from_user.mention, str(message.from_user.id))
    command, recipient = await get_command(message)
    logger.debug(f'recipient: {recipient}')

    user_id_ = await get_mentioned_user(recipient)
    logger.debug(f'user_id: {user_id_}')

    # user_id = message.from_user.id
    # logger.debug(f'user_id: {user_id}')
    path = 'meme_entries'
    image = f'image-{user_id_}.jpg'
    try:
        if os.path.exists(f'./{path}/{image}'):
            with open(f'{path}/{image}', "r+b") as photo:
                await message.reply_photo(photo, caption=f"Meme Entry by {recipient}")
            # await message.reply_photo(os.open(image, 'rb'))
        else:
            await message.reply(f'{recipient}, has no entry for the Meme Contest.')
    except Exception as exc:
        await message.reply(f'{recipient} Entry View failed. {exc}')


# @dp.message_handler(commands=["vote"])
# async def vote(message: types.Message):
#     # pair the user_name with user_id
#     await redis.set_value(message.from_user.mention, str(message.from_user.id))

#     if message.from_user.is_bot:
#         await message.reply(f'{message.from_user.mention}, bots cannot vote!')
#         return

#     msg_sender = message.from_user.id
#     logger.debug(f'msg_sender: {msg_sender}')

#     voted = await redis.get_value(f'{str(message.from_user.id)}_voted')
#     logger.debug(f'voted: {voted}')

#     command, recipient = await get_command(message)

#     if (recipient is None) or (recipient == ""):
#         await message.reply(f'Sorry {message.from_user.mention}, you must select a user to vote for. Like so, "/vote @username".')
#         return

#     if (voted is None) or (int(voted) == 0):
#         if command != '/vote':
#             await message.reply('How did this get here?')
#         else:
#             # inc number of recipient votes
#             vote = f'{recipient}_votes'
#             redis_return = await redis.inc_value(vote)
#             # mark the user as having voted once
#             voter = f'{msg_sender}_voted'
#             redis_return2 = await redis.inc_value(voter)
#             # Save who the user voted for
#             redis_return3 = await redis.set_value(str(msg_sender), recipient)
#             await message.reply(f'✅ Thank You {message.from_user.mention} for Voting')
#             logger.debug(f'redis_return for redis.inc_value(s): {redis_return} {redis_return2} {redis_return3}')
#     elif int(voted) >= 1:
#         voted_for_member = await redis.get_value(str(message.from_user.id))
#         logger.debug(f'voted for member: {voted_for_member}')
#         user_id_ = await get_mentioned_user(voted_for_member)
#         logger.debug(f'user_id_return_from_get_chat_member: {user_id_}')
#         if user_id_ is not None:
#             member = await bot.get_chat_member(chat_id=message.chat.id, user_id=user_id_)
#             logger.debug(f'member: {member}')
#             await message.reply(f'Sorry {message.from_user.mention}, you have already voted. You voted for {member.user.mention}')
#         else:
#             await redis.set_value(str(recipient), 'unknown')
#             # inc number of recipient votes
#             vote = f'{recipient}_votes'
#             redis_return = await redis.inc_value(vote)
#             # mark the user as having voted once
#             voter = f'{msg_sender}_voted'
#             redis_return2 = await redis.inc_value(voter)
#             # Save who the user voted for
#             redis_return3 = await redis.set_value(str(msg_sender), recipient)
#             await message.reply(f'✅ Thank You {message.from_user.mention} for Voting')
#             logger.debug(f'redis_return for redis.inc_value(s): {redis_return} {redis_return2} {redis_return3}')

#             # await message.reply(f'Sorry {message.from_user.mention}, you cannot vote for that member, they need to send a message to the chat to be eligible.')


# @dp.message_handler(commands=["delete_vote"])
# async def del_vote(message: types.Message):
#     # pair the user_name with user_id
#     await redis.set_value(message.from_user.mention, str(message.from_user.id))

#     msg_sender = message.from_user.id
#     logger.debug(f'msg_sender: {msg_sender}')

#     voted_state = await redis.get_value(f'{str(message.from_user.id)}_voted')
#     logger.debug(f'voted: {voted_state}')
#     if (voted_state is None) or (int(voted_state) == 0):
#         await message.reply(f'{message.from_user.mention}, you have not voted yet!')
#     elif int(voted_state) >= 1:
#         # remove 1 vote from user
#         await redis.set_value(f'{str(message.from_user.id)}_voted', str(int(voted_state) - 1))

#         # get the person our user voted for
#         voted_for = await redis.get_value(f'{str(msg_sender)}')

#         # get number of votes for person that user voted for
#         num_votes = await redis.get_value(f'{voted_for}_votes')
#         logger.debug(f'num_votes: {num_votes}')

#         # remove vote from person voted_for
#         await redis.set_value(f'{voted_for}_votes', str(int(num_votes) - 1))

#         # change vote to empty
#         await redis.set_value(f'{str(msg_sender)}', '0')
#         await message.reply(f'{message.from_user.mention}, you have deleted your vote!')
#     else:
#         await message.reply(f'{message.from_user.mention}, something went wrong')


@dp.message_handler(commands=["results"], is_admin=True)
async def get_votes(message: types.Message):
    votes = await redis.get_keys('*_votes')
    logger.debug(f'votes: {votes}')
    vote_tally = {}
    if votes is None:
        await message.reply('There are no votes.')
    else:
        for telegram_user in votes:
            num_votes = await redis.get_value(telegram_user)
            vote_tally[telegram_user] = num_votes
        sorted_votes = sorted(vote_tally.items(), key=lambda x: x[1], reverse=True)
        logger.debug(f'sorted_votes: {sorted_votes}')
        for vote in sorted_votes:
            (user_, votes_) = vote
            if (votes_ != '0') and (user_ is not None) and (user_ != "_votes"):
                size = len(user_)
                user_id_ = await get_mentioned_user(user_[:size - 6])
                try:
                    if get_mentioned_user is not None:
                        member = await bot.get_chat_member(chat_id=message.chat.id, user_id=user_id_)
                        await bot.send_message(chat_id=message.chat.id, text=f'{member.user.mention} has {votes_} vote(s).')
                except Exception:
                    await bot.send_message(chat_id=message.chat.id, text=f'{user_[:size - 6]} has {votes_} votes(s).')


@dp.message_handler(commands=['voters_list'], is_admin=True)
async def get_voters(message: types.Message):
    voted_list = await redis.get_keys('*_voted')
    logger.debug(f'Voted list: {voted_list}')
    with open('vote_data.json', 'w') as outfile:
        votes = []
        i = 1
        for vote in voted_list:
            vote_package = {}
            vote_package['user_id'] = vote[:len(vote) - 6]
            vote_package['voted_for'] = await redis.get_value(vote_package['user_id'])
            try:
                user_info = await bot.get_chat_member(-1001519982064, vote_package['user_id'])
                logger.debug(user_info)
                vote_package['user_info'] = user_info.to_python()
                # logger.debug(f'user_info: {user_info.to_dict()}')
                # vote_package['user_name'] = user_info['result']['user']['username']
                # vote_package['first_name'] = user_info['result']['user']['first_name']
                # vote_package['last_name'] = user_info['result']['user']['last_name']
                # vote_package['is_bot'] = user_info['result']['user']['is_bot']
            except Exception:
                vote_package['user_info'] = str('Cannot Find in Chat')
            votes.append(vote_package)
            i += 1
            # await bot.send_message(chat_id=message.chat.id, text=f'{user} voted for {voted_for}')
        # Directly from dictionary
        json.dump(votes, outfile)

    # Opening JSON file and loading the data
    # into the variable data
    with open('vote_data.json') as json_file:
        jsondata = json.load(json_file)

    data_file = open('vote_data.csv', 'w', newline='')
    csv_writer = csv.writer(data_file)

    count = 0
    for data in jsondata:
        if count == 0:
            header = data.keys()
            csv_writer.writerow(header)
            count += 1
        csv_writer.writerow(data.values())

    data_file.close()

    with open('vote_data.csv', 'r+b') as voter_data:
        await message.reply_document(voter_data, caption='vote_data.csv')


@dp.message_handler(commands=["hits"])
async def get_hits(message: types.Message):
    hits = await redis.get_value(f'{str(message.from_user.id)}_hits')
    await message.reply(f'{message.from_user.mention} has {hits} hits.')


@dp.message_handler(chat_type=ChatType.SUPERGROUP)
async def add_hit(message: types.Message):
    # pair the user_name with user_id
    await redis.set_value(message.from_user.mention, str(message.from_user.id))

    user_hit = f'{str(message.from_user.id)}_hits'
    logger.debug(f'user_hit: {user_hit}')
    redis_return = await redis.inc_value(user_hit)
    logger.debug(f'redis_return for redis.inc_value: {redis_return}')

    if not message.from_user.is_bot:
        total_return = await redis.inc_value('Total_Hits')
        logger.debug(f'total_return for redis.inc_value: {total_return}')

if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=False)
