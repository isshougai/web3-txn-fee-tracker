from typing import Any
from binance.spot import Spot as Client
from datetime import datetime

spot_client = Client(base_url="https://data-api.binance.vision")

def get_ethusdt_price():
    test_time = datetime.now()
    timestamp = int(test_time.timestamp() * 1000)
    print(timestamp)
    print(spot_client.time())
    print(spot_client.klines(symbol="ETHUSDT", interval="1s", startTime=1650540260000, endTime=1650540260000))