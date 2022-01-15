from curses import keyname
import json
from eospy.cleos import Cleos
from eospy.keys import EOSKey, check_wif

from utils.logger import logger as Logger

logger = Logger

ce = Cleos(url='https://ore.openrights.exchange')

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

    # check = EOSKey.to_public(key)
    # logger.debug(f'to_public of private key: {check}')

    # wif = EOSKey.to_wif(key)
    # logger.debug(f'to_wif of key: {wif}')

    # key_pair['public'] = ce.create_key()
    # logger.debug(f'Cleos generated public key: {key_pair["public"]}')

    # key_pair['private'] = EOSKey.to_wif(key_pair['public'])
    # logger.debug(f'wif2: {key_pair["private"]}')

    return key_pair