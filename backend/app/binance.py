from typing import Any, Dict, List
from binance.spot import Spot as Client
from datetime import datetime, timezone
from app import crud
from app.models import SpotPriceCreate

from sqlmodel import Session

ONE_SECOND_MS = 1000
ETH_USDT_SYMBOL = "ETHUSDT"

spot_client = Client(base_url="https://data-api.binance.vision")

def get_ethusdt_price(*, session: Session, timestamps_ms: List[int]) -> Dict[int, float]:
    """
    Retrieves the spot price of ETHUSDT from Binance API for a given list of timestamps.
    """
    prices = {}
    timestamps = [datetime.fromtimestamp(ts / ONE_SECOND_MS, tz=timezone.utc) for ts in timestamps_ms]

    # Check if prices are already in the database
    db_spot_prices = crud.get_spot_prices(session=session, symbol=ETH_USDT_SYMBOL, timestamps=timestamps)
    for price in db_spot_prices:
        prices[int(price.timestamp.astimezone(timezone.utc).timestamp() * ONE_SECOND_MS)] = price.price
    
    found_db_prices = set(prices.keys())
    missing_prices = set(timestamps_ms) - found_db_prices if timestamps_ms else set()

    # Return if all prices are found in the database
    if not missing_prices:
        return prices

    # Get the earliest and latest timestamps
    start_time = min(missing_prices)
    end_time = max(missing_prices)

    max_interval = 1000 * ONE_SECOND_MS 

    new_spot_prices = []
    current_start_time = start_time

    # Get missing prices from Binance API
    while current_start_time <= end_time:
        current_end_time = min(current_start_time + max_interval, end_time)

        klines = spot_client.klines(symbol=ETH_USDT_SYMBOL, interval="1s", startTime=current_start_time, endTime=current_end_time, limit=1000)
        for kline in klines:
            kline_open_time = kline[0]
            open_price = float(kline[1])
            timestamp = datetime.fromtimestamp(kline_open_time / ONE_SECOND_MS, tz=timezone.utc)
            if kline_open_time in missing_prices:
                new_spot_price = SpotPriceCreate(symbol=ETH_USDT_SYMBOL, timestamp=timestamp, price=open_price)
                new_spot_prices.append(new_spot_price)
                prices[kline_open_time] = open_price

        current_start_time = current_end_time + ONE_SECOND_MS

    # Batch insert new spot prices into the database
    if new_spot_prices:
        crud.insert_spot_prices(session=session, spot_prices_create=new_spot_prices)

    return prices

def batch_save_ethusdt_price(*, session: Session, start_time: datetime, end_time: datetime) -> None:
    """
    Retrieves and saves the spot price of ETHUSDT from Binance API for a given start and end time.
    """
    start_time_ms = int(start_time.astimezone(timezone.utc).timestamp() * ONE_SECOND_MS)
    end_time_ms = int(end_time.astimezone(timezone.utc).timestamp() * ONE_SECOND_MS)

    max_interval = 1000 * ONE_SECOND_MS 

    new_spot_prices = []
    current_start_time = start_time_ms

    while current_start_time <= end_time_ms:
        current_end_time = min(current_start_time + max_interval, end_time_ms)

        # Get spot prices from Binance API
        klines = spot_client.klines(symbol=ETH_USDT_SYMBOL, interval="1s", startTime=current_start_time, endTime=current_end_time, limit=1000)
        for kline in klines:
            kline_open_time = kline[0]
            open_price = float(kline[1])
            timestamp = datetime.fromtimestamp(kline_open_time / ONE_SECOND_MS, tz=timezone.utc)
            new_spot_price = SpotPriceCreate(symbol=ETH_USDT_SYMBOL, timestamp=timestamp, price=open_price)
            new_spot_prices.append(new_spot_price)

        # Move to the next chunk
        current_start_time = current_end_time + ONE_SECOND_MS

    # Batch insert new spot prices into the database
    if new_spot_prices:
        crud.insert_spot_prices(session=session, spot_prices_create=new_spot_prices)