from datetime import datetime

from utils.cmc import OREPrice

async def check_expiry(latest_price: OREPrice) -> None:
    time_diff = datetime.now() - latest_price.datetime
    if latest_price.price == 0.0:
        await latest_price.update_price()
    elif time_diff.total_seconds() >= 60:
        await latest_price.update_price()
