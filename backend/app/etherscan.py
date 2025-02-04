from datetime import datetime, timezone
from typing import List
import httpx
from sqlmodel import Session
from app.binance import get_ethusdt_price
from app.core.config import settings
from app.models import TransactionCreate


ONE_SECOND_MS = 1000

def get_block_no_by_timestamp(*, client: httpx.Client, timestamp: int) -> int:
    """
    Retrieves the block number from Etherscan API for a given timestamp.
    """
    url = f"{settings.ETHERSCAN_URL}?module=block&action=getblocknobytime&timestamp={timestamp}&closest=before&apikey={settings.ETHERSCAN_API_KEY}"
    response = client.get(url)
    data = response.json()
    
    if "result" not in data:
        raise ValueError(f"Unexpected response format: {data}")
    
    if data["result"].isdigit():
        return int(data["result"])
    else:
        raise ValueError(data["result"])

def get_erc20_token_transfer_events(
    *,
    client: httpx.Client,
    session: Session,
    address: str,
    from_block: int,
    to_block: int
) -> List[TransactionCreate]:
    """
    Retrieves ERC20 token transfer events from Etherscan API for a given contract address and block range.
    """
    transactions = []
    page = 1
    offset = 100
    timestamps_ms = []
    raw_transactions = []

    while True:
        url = (
            f"{settings.ETHERSCAN_URL}?module=account&action=tokentx"
            f"&address={address}"
            f"&page={page}&offset={offset}&startblock={from_block}&endblock={to_block}"
            f"&sort=desc&apikey={settings.ETHERSCAN_API_KEY}"
        )

        response = client.get(url)
        response.raise_for_status()
        data = response.json()

        if not data["result"]:
            break

        for event in data["result"]:
            timestamp_ms = int(event["timeStamp"]) * ONE_SECOND_MS
            timestamps_ms.append(timestamp_ms)
            raw_transactions.append(event)

        page += 1

    # Fetch all ETH/USDT prices for the collected timestamps
    eth_usdt_prices = get_ethusdt_price(session=session, timestamps_ms=timestamps_ms)

    # Process the raw transactions to create TransactionCreate objects
    for event in raw_transactions:
        timestamp_ms = int(event["timeStamp"]) * ONE_SECOND_MS
        eth_usdt_price = eth_usdt_prices.get(timestamp_ms)

        transaction = TransactionCreate(
            tx_hash=event["hash"],
            timestamp=datetime.fromtimestamp(int(event["timeStamp"]), tz=timezone.utc),
            txn_fee_usdt=float(event["gasUsed"]) * float(event["gasPrice"]) * eth_usdt_price / 1e18,
            gas_used=int(event["gasUsed"]),
            gas_price_wei=int(event["gasPrice"]),
            txn_fee_eth=float(event["gasUsed"]) * float(event["gasPrice"]) / 1e18,
            eth_usdt_price=eth_usdt_price
        )
        transactions.append(transaction)

    return transactions