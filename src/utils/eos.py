from eospy.cleos import Cleos
from eospy.keys import EOSKey, check_wif
import os

from utils.logger import logger as Logger

logger = Logger

ce = Cleos(os.getenv('CLEOS_URL'))


def get_info() -> dict:
    get_info = ce.get_info()
    logger.debug(get_info)
    return get_info


def get_balance(account: str) -> list:
    kwargs = {
        "account": account,
        "code": "eosio.token",
        "symbol": "ORE"
    }
    get_bal = ce.get_currency_balance(**kwargs)
    logger.debug(get_bal)
    return get_bal


def create_new_keypair() -> dict:
    """
    Generate an EOS compatable public/private key pair.
    """
    public_key = EOSKey()
    logger.debug(f'Public Key: {public_key}')

    private_key = public_key.to_wif()
    logger.debug(f'Private Key: {private_key}')

    key_pair = {'private': private_key, 'public': public_key}

    logger.debug(check_wif(private_key))

    return key_pair
