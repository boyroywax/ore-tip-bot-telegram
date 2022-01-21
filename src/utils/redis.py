import asyncio_redis
import json
import time
import re

from conf import config as c
from resources import logger as Logger
from utils import helpers

helpers = helpers.Helpers()
logger = Logger

currency_symbol = c.currency_symbol

# TIPBOT LEGACY CODE
REDIS_HOST = c.redis_host
REDIS_PORT = c.redis_port


class Redis():
    def __init__(self):
        self.host = c.redis_host
        self.port = c.redis_port

    async def createConnection(self):
        return await asyncio_redis.Connection.create(
            host=self.host,
            port=self.port
        )

    # Redis Functions
    async def publish(self, channel, message):
        """Publish events to the pub-sub channel."""
        try:
            connection = await self.createConnection()
            # Create publish on the feed
            message = str(message)
            await connection.publish(channel, message)
            connection.close()
            return True
        except Exception as err:
            logger.error('Error in publish - {}'.format(err))
            return False

    # Lower Level Interaction with wallet Redis Protocol
    async def sendCommand(self, msg_id, command) -> bool:
        """Sends a command to the wallet, returns send status

        Expects Channel: Wallet.<currency_symbol>
                Content: message_id command arg1 arg2 ...
        """
        message = str(msg_id) + ' ' + str(command)
        sub_channel = str('Wallet.') + str(currency_symbol)
        message_published = await self.publish(sub_channel, message)
        return message_published

    async def subscribeToChannel(self, channel):
        connection = await self.createConnection()
        subscriber = await connection.start_subscribe()
        await subscriber.subscribe([channel])
        return subscriber

    async def getValue(self, my_key) -> str:
        """Retrive a key: value pair"""
        try:
            # Create Redis connection
            connection = await self.createConnection()
            # Get a key
            retrievedValue = await connection.get(my_key)
            await connection.delete([my_key])
            # When finished, close the connection.
            connection.close()
        except Exception:
            retrievedValue = None
        return retrievedValue

    async def command(self, command):
        """Run  a command on the wallet and receive the output"""
        sub_channel = 'Wallet.' + currency_symbol + '.Output'
        subscriber = await self.subscribeToChannel(sub_channel)
        msg_id = await helpers.createMessageID()
        await self.sendCommand(msg_id, command)
        while True:
            reply = await subscriber.next_published()
            # Check the  message id's
            if reply.value.startswith(msg_id):
                # Strip down to the the mongo id
                validation = re.sub(r'^\W*\w+\W*', '', reply.value)
                # logger.debug(f'validation: {validation}')
                if validation:
                    result = await self.getValue(msg_id)
                    logger.debug(f'result: {result}')
                    return result

    async def verifyWithdrawPayload(self, payload):
        # Split the payload
        try:
            # split_p = payload.split('_')
            address = payload['address']
            value = payload['amount']
        except Exception:
            return None, None

        # Make sure the address is valid
        if await self.validateAddress(address):
            # Check that amount is valid (< 0 and < wallet_total)
            logger.debug(f'address {address} is valid')
            wallet_total = await self.getBalance()
            if (value > 0.0) and (value < float(wallet_total)):
                return address, value
        else:
            return None, None

    async def validateAddress(self, address):
        try:
            command = 'getaddressinfo' + ' ' + address
            command_output = await self.command(command)
            command_output = json.loads(command_output)
            logger.debug('command_output {}'.format(command_output))
            if command_output['address'] == address:
                return True
            else:
                return False
        except Exception:
            # logger.debug('"getaddressinfo" command not found, running "validateaddress" instead...')
            command = 'validateaddress' + ' ' + address
            # logger.debug('exception thrown: {}'.format(exc))
            validate_ad = await self.command(command)
            validate_ad = json.loads(validate_ad)
            if validate_ad['isvalid'] is True:
                logger.debug('address is valid')
                return True
            else:
                return False

    # Wallet Functions
    async def getBalance(self):
        """Check the balance in the wallet"""
        command = 'getbalance'
        command_output = await self.command(command)
        logger.debug('getbalance command output {}'.format(command_output))
        return command_output

    async def getBlock(self, block_hash):
        command = 'getblock' + ' ' + str(block_hash)
        return await self.command(command)

    async def getBlockByHeight(self, block_height):
        block_hash = await self.getBlockHash(block_height)
        return await self.getBlock(block_hash)

    async def getBlockHash(self, block_index):
        command = 'getblockhash' + ' ' + str(block_index)
        return await self.command(command)

    async def getBlockHeight(self):
        command = 'getblockcount'
        return await self.command(command)

    async def getInfo(self):
        command = 'getinfo'
        return await self.command(command)

    async def getTransactionList(self):
        command = 'listtransactions'
        result = await self.command(command)
        logger.debug(f'getTransanctionList result: {result}')
        return result

    async def getLatestBlock(self):
        block_height = await self.getBlockHeight()
        return await self.getBlockByHeight(block_height)

    async def getNewAddress(self):
        command = 'getnewaddress'
        return await self.command(command)

    async def getTransaction(self, txid):
        command = 'gettransaction' + ' ' + str(txid)
        return await self.command(command)

    async def getTxFee(self):
        command = 'getinfo'
        result = await self.command(command)
        result = json.loads(result)
        txfee = result['paytxfee']
        # txfee = command_output['paytxfee']
        return {'value': str(txfee)}

    async def setTxFee(self, amount):
        command = 'settxfee' + ' ' + str(amount)
        result = await self.command(command)
        return {'output': result}

    async def sendToAddress(self, payload) -> str:
        """Withdraw coins from the wallet"""
        # Check the payload
        address, amount = await self.verifyWithdrawPayload(payload)
        if address is not None:
            command = 'sendtoaddress' + ' ' + '"' + str(address) + '"' + ' ' + str(amount)
            result = await self.command(command)
            logger.debug(f'result of command: {result}')
            return {'output': result}
        else:
            return {'ouput': "error"}

    # Key-Values Section
    async def setValue(self, my_key, my_value) -> bool:
        try:
            # Create Redis connection
            connection = await asyncio_redis.Connection.create(
                host=REDIS_HOST,
                port=REDIS_PORT)
            # Increment a key
            await connection.set(my_key, my_value)
            # When finished, close the connection.
            connection.close()
            return True
        except Exception:
            return False

    async def incValue(self, my_key) -> bool:
        try:
            # Create Redis connection
            connection = await asyncio_redis.Connection.create(
                host=REDIS_HOST,
                port=REDIS_PORT)
            # Increment a key
            await connection.incr(my_key)
            # When finished, close the connection.
            connection.close()
            return True
        except Exception:
            return False

    # async def getValue(self, my_key) -> str:
    #     try:
    #         # Create Redis connection
    #         connection = await asyncio_redis.Connection.create(
    #             host=REDIS_HOST,
    #             port=REDIS_PORT)
    #         # Get a key
    #         retrievedValue = await connection.get(my_key)
    #         # When finished, close the connection.
    #         connection.close()
    #     except Exception:
    #         retrievedValue is None
    #     return retrievedValue

# Hash Section

    async def setHash(self, my_key, my_field, my_value) -> int:
        # Create Redis connection
        try:
            connection = await asyncio_redis.Connection.create(
                host=REDIS_HOST,
                port=REDIS_PORT)
            # Set a hash field
            hashResponse = await connection.hset(my_key, my_field, my_value)
            # When finished, close the connection.
            connection.close()
            return hashResponse
        except Exception:
            hashResponse = 0
            return hashResponse

    async def setHashMaps(self, my_key, my_dict) -> bool:
        try:
            # Create Redis connection
            connection = await asyncio_redis.Conection.create(
                host=REDIS_HOST,
                port=REDIS_PORT)
            # Get a key
            await connection.hmset(my_key, my_dict)
            # When finished, close the connection.
            connection.close()
            return True
        except Exception:
            return False

    async def getHash(self, my_key, my_field) -> str:
        retrievedValue = None
        try:
            # Create Redis connection
            connection = await asyncio_redis.Connection.create(
                host=REDIS_HOST,
                port=REDIS_PORT)
            # Get a key
            retrievedValue = await connection.hget(my_key, my_field)
            # When finished, close the connection.
            connection.close()
        except Exception:
            retrievedValue is None
        return retrievedValue

    async def existsHash(self, my_key, my_field) -> bool:
        try:
            # Create Redis connection
            connection = await asyncio_redis.Connection.create(
                host=REDIS_HOST,
                port=REDIS_PORT)
            # Get a key
            valueExists = await connection.hexists(my_key, my_field)
            # When finished, close the connection.
            connection.close()
        except Exception:
            valueExists is False
        return valueExists

    async def hashScan(self, query) -> list:
        user_list = []
        try:
            connection = await asyncio_redis.Connection.create(
                host=REDIS_HOST,
                port=REDIS_PORT)
            cursor = await connection.scan(match=query)
            while True:
                item = await cursor.fetchone()
                if item is None:
                    break
                else:
                    user_list.append(str(item))
        except Exception:
            user_list.append("No Keys")
        return user_list

    async def hashSetScan(self, key, query) -> list:
        user_list = []
        try:
            connection = await asyncio_redis.Connection.create(
                host=REDIS_HOST,
                port=REDIS_PORT)
            cursor = await connection.hscan(key, match=query)
            user_list = await cursor.fetchall()
            # while True:
            #     item = await cursor.fetchone()
            #     if item is None:
            #         break
            #     else:
            #         user_list.append(str(item))
        except Exception:
            user_list.append("No Keys")
        return user_list

    async def delHashSet(self, my_key, fields) -> int:
        # Create Redis connection
        try:
            connection = await asyncio_redis.Connection.create(
                host=REDIS_HOST,
                port=REDIS_PORT)
            # Set a hash field
            hashResponse = await connection.hdel(my_key, fields)
            # When finished, close the connection.
            connection.close()
        except Exception:
            hashResponse = 0
        return hashResponse

    async def flushall(self):
        """Removes all entries from the Redis DB"""
        try:
            connection = await asyncio_redis.Connection.create(
                host=REDIS_HOST,
                port=REDIS_PORT)
            # Set a hash field
            hashResponse = await connection.flushall()
            connection.close()
        except Exception:
            hashResponse = 0
        return hashResponse

    async def add_hit(self, ctx):
        """ Increment user hit and Total hit"""
        # increment user hit
        user_hits = str(ctx.author.id) + "_hits"
        logger.info('User hit being added to Redis - {}'.format(user_hits))
        inc_user_value = await self.incValue(user_hits)

        if inc_user_value is True:
            logger.info(
                'The Bot has interecpted a message and registered a hit for user'
            )
        else:
            logger.error(
                'The bot intercepted a message but could not register a hit for user'
            )

        # register hit to total count
        total_hits = await self.incValue('hits')

        if total_hits is True:
            logger.info(
                'The Bot has interecpted a message and incremented the Server Total'
            )
        else:
            logger.error(
                'The bot intercepted a message but could not increment the Server Total'
            )

        #  register hit to channel_hits
        channel_key = str(ctx.channel.id) + "_hits"
        hit_time = str(time.time())
        user_id = str(ctx.author.id)
        channel_hit_register = await self.setHash(
            channel_key, user_id, hit_time
        )

        if channel_hit_register != 0:
            logger.info(
                'The Bot has interecpted a message and updated the channelid_hit datetime. - {}'.format(
                    channel_hit_register
                )
            )
        else:
            logger.error(
                'The bot intercepted a message but could not update the channelid_hit datetime. - {}'.format(
                    channel_hit_register
                )
            )

# PUB-SUB Section
    # async def publish(self, channel, message):
    #     """Read events from pub-sub channel."""
    #     try:
    #         connection = await asyncio_redis.Connection.create(
    #             host=REDIS_HOST,
    #             port=REDIS_PORT)
    #         # Create subscriber.
    #         logger.info(
    #             'connection created to redis from publish {}'.format(
    #                 connection
    #             )
    #         )
    #         # Create publish on the feed
    #         message = str(message)
    #         await connection.publish(channel, message)
    #         connection.close()
    #         return True
    #     except Exception:
    #         return False
    #     logger.info(
    #         '{}, message has been published to redis'.format(message)
    #     )

    async def start_pubsub(self, sub_channel):
        """Start Subscriber to a PubSub Channel"""
        connection = await asyncio_redis.Connection.create(
            host=REDIS_HOST,
            port=REDIS_PORT)
        logger.debug('Redis Connection Succeeded')

        # create redis subscription to pubsub
        subscriber = await connection.start_subscribe()
        await subscriber.subscribe([sub_channel])
        logger.debug('subscribed to channel')

        # Wait for messages
        while True:
            # Get the next reply
            reply = await subscriber.next_published()
            logger.debug('Message received {}'.format(reply))

            # Value is message id
            value = reply.value
            value = str(value)
            logger.debug('Value from Pubsub - {}'.format(value))

        connection.close()
