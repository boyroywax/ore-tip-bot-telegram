import asyncio_redis
import os

from utils.logger import logger as Logger

logger = Logger


class Redis():
    def __init__(self):
        self.host = str(os.getenv('REDIS_HOST'))
        self.port = int(os.getenv('REDIS_PORT'))
        logger.debug(f'{self.host}{self.port}')

    async def create_connection(self):
        return await asyncio_redis.Connection.create(
            host=self.host,
            port=self.port
        )

    async def start_pubsub(self, sub_channel: list):
        """Start Subscriber to a PubSub Channel"""
        connection = await self.create_connection()
        logger.info('Redis Connection Succeeded')

        # create redis subscription to pubsub
        subscriber = await connection.start_subscribe()
        await subscriber.subscribe(sub_channel)
        logger.debug(f'subscribed to channel: {sub_channel}')
        return connection, subscriber

    async def stop_pubsub(self, connection):
        connection.close()

    async def get_next_published(self, subscriber):
        # Get the next reply
        reply = await subscriber.next_published()
        logger.debug('Message received {}'.format(reply))

        # Value is message id
        value = reply.value
        value = str(value)
        logger.debug('Value from Pubsub - {}'.format(value))
        return reply

        # Redis Functions
    async def publish(self, channel, message) -> bool:
        """Publish events to the pub-sub channel."""
        try:
            connection = await self.create_connection()
            # Create publish on the feed
            message = str(message)
            await connection.publish(channel, message)
            connection.close()
            return True
        except Exception as err:
            logger.error('Error in publish - {}'.format(err))
            return False

    async def get_value(self, my_key) -> str:
        """Retrive a key: value pair"""
        try:
            connection = await self.create_connection()
            # Get a key
            retrieved_value = await connection.get(my_key)
            await connection.delete([my_key])
            connection.close()
        except Exception as exc:
            logger.error(f'get_value Exception: {exc}')
            retrieved_value = None
        return retrieved_value

    # Key-Values Section
    async def set_value(self, my_key, my_value) -> bool:
        try:
            connection = await self.create_connection()
            # Set a key
            await connection.set(my_key, my_value)
            connection.close()
            return True
        except Exception as exc:
            logger.debug(f'set_value Exception: {exc}')
            return False

    async def inc_value(self, my_key: str) -> bool:
        try:
            connection = await self.create_connection()
            # Increment a key
            await connection.incr(my_key)
            connection.close()
            return True
        except Exception as exc:
            logger.error(f'inc_value is failing: {exc}')
            return False

# Hash Section
    async def set_hash(self, my_key, my_field, my_value) -> int:
        # Create Redis connection
        try:
            connection = await self.create_connection()
            # Set a hash field
            hash_response = await connection.hset(my_key, my_field, my_value)
            connection.close()
            return hash_response
        except Exception as exc:
            logger.error(f'set_hash: {exc}')
            hash_response = 0
            return hash_response

    async def set_hashmaps(self, my_key, my_dict) -> bool:
        try:
            connection = await self.create_connection()
            # Get a key
            await connection.hmset(my_key, my_dict)
            connection.close()
            return True
        except Exception as exc:
            logger.error(f'Set hashmaps: {exc}')
            return False

    async def get_hash(self, my_key, my_field) -> str:
        retrieved_value = None
        try:
            connection = await self.create_connection()
            # Get a key
            retrieved_value = await connection.hget(my_key, my_field)
            connection.close()
        except Exception as exc:
            logger.error(f'gat_hash: {exc}')
            retrieved_value is None
        return retrieved_value

    async def exists_hash(self, my_key, my_field) -> bool:
        try:
            connection = await self.create_connection()
            # Get a key
            value_exists = await connection.hexists(my_key, my_field)
            connection.close()
        except Exception as exc:
            logger.error(f'exists_hash: {exc}')
            value_exists is False
        return value_exists

    async def hash_scan(self, query) -> list:
        user_list = []
        try:
            connection = await self.create_connection()
            cursor = await connection.scan(match=query)
            while True:
                item = await cursor.fetchone()
                if item is None:
                    break
                else:
                    user_list.append(str(item))
        except Exception as exc:
            logger.error(f'hash scan: {exc}')
            user_list.append("No Keys")
        return user_list

    async def hash_set_scan(self, key, query) -> list:
        user_list = []
        try:
            connection = await self.create_connection()
            cursor = await connection.hscan(key, match=query)
            user_list = await cursor.fetchall()
            # while True:
            #     item = await cursor.fetchone()
            #     if item is None:
            #         break
            #     else:
            #         user_list.append(str(item))
        except Exception as exc:
            logger.error(f'hash_set_scan: {exc}')
            user_list.append("No Keys")
        return user_list

    async def del_hash_set(self, my_key, fields) -> int:
        # Create Redis connection
        try:
            connection = await self.create_connection()
            # Set a hash field
            hash_response = await connection.hdel(my_key, fields)
            connection.close()
        except Exception as exc:
            logger.error(f'del_hash_set: {exc}')
            hash_response = 0
        return hash_response

    async def flush_all(self):
        """Removes all entries from the Redis DB"""
        try:
            connection = await self.create_connection()
            # Set a hash field
            hash_response = await connection.flushall()
            connection.close()
        except Exception as exc:
            hash_response = 0
        return hash_response

    # async def add_hit(self, ctx):
    #     """ Increment user hit and Total hit"""
    #     # increment user hit
    #     user_hits = str(ctx.author.id) + "_hits"
    #     logger.info('User hit being added to Redis - {}'.format(user_hits))
    #     inc_user_value = await self.inc_value(user_hits)

    #     if inc_user_value is True:
    #         logger.info(
    #             'The Bot has interecpted a message and registered a hit for user'
    #         )
    #     else:
    #         logger.error(
    #             'The bot intercepted a message but could not register a hit for user'
    #         )

    #     # register hit to total count
    #     total_hits = await self.inc_value('hits')

    #     if total_hits is True:
    #         logger.info(
    #             'The Bot has interecpted a message and incremented the Server Total'
    #         )
    #     else:
    #         logger.error(
    #             'The bot intercepted a message but could not increment the Server Total'
    #         )

    #     #  register hit to channel_hits
    #     channel_key = str(ctx.channel.id) + "_hits"
    #     hit_time = str(time.time())
    #     user_id = str(ctx.author.id)
    #     channel_hit_register = await self.set_hash(
    #         channel_key, user_id, hit_time
    #     )

    #     if channel_hit_register != 0:
    #         logger.info(
    #             'The Bot has interecpted a message and updated the channelid_hit datetime. - {}'.format(
    #                 channel_hit_register
    #             )
    #         )
    #     else:
    #         logger.error(
    #             'The bot intercepted a message but could not update the channelid_hit datetime. - {}'.format(
    #                 channel_hit_register
    #             )
    #         )
