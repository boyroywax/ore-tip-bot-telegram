import json
from eospy.cleos import Cleos


from utils.logger import logger as Logger

logger = Logger

ce = Cleos(url='https://ore.openrights.exchange')

def get_info() -> json:
    get_info = ce.get_info()
    logger.debug(get_info)
    return get_info

def get_balance(account: str):
    args = {
        "account": account,
        "code": "eosio.token",
        "symbol": "ORE"
    }
    get_bal = ce.get_currency_balance(**args)
    logger.debug(get_bal)
    return get_bal