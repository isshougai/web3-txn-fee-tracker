from sqlmodel import Session
from web3 import Web3
from web3.exceptions import TransactionNotFound, BlockNotFound
from app.core.config import settings
from app.binance import get_ethusdt_price
from datetime import datetime, timezone
from typing import Any, List, Optional

from app.models import TransactionCreate, TransactionsPublic
from app.crud import get_transactions, insert_transactions

ONE_SECOND_MS = 1000

web3 = Web3(Web3.HTTPProvider(settings.INFURA_HTTPS))

def get_eth_transaction_detail_for_insert(*, session: Session, tx_hash: str) -> TransactionCreate:
    """
    Retrieves and displays details for a given Ethereum transaction hash for inserting into DB.
    """
    if not web3.is_connected():
        raise ConnectionError("Failed to connect to the Ethereum node.")
    
    try:
        tx = web3.eth.get_transaction(tx_hash)
        tx_receipt = web3.eth.get_transaction_receipt(tx_hash)
        block = web3.eth.get_block(tx['blockNumber'])
        timestamp = block['timestamp']
        timestamp_ms = timestamp * ONE_SECOND_MS

        gas_used = tx_receipt['gasUsed']
        total_gas_cost_eth = web3.from_wei(tx['gasPrice'] * gas_used, 'ether')

        eth_price_usd = get_ethusdt_price(session=session, timestamps_ms=[timestamp_ms]).get(timestamp_ms)
        total_gas_cost_usd = float(total_gas_cost_eth) * eth_price_usd

        transaction = TransactionCreate(
            tx_hash=tx.hash.to_0x_hex(),
            timestamp=datetime.fromtimestamp(timestamp, tz=timezone.utc),
            txn_fee_usdt=total_gas_cost_usd,
            gas_used=gas_used,
            gas_price_wei=tx['gasPrice'],
            txn_fee_eth=total_gas_cost_eth,
            eth_usdt_price=eth_price_usd
        )

        return transaction

    except TransactionNotFound:
        raise ValueError(f"Transaction with hash {tx_hash} not found.")
    except BlockNotFound:
        raise ValueError(f"Block containing transaction {tx_hash} not found.")
    except RuntimeError as re:
        raise re
    except Exception as err:
        raise RuntimeError(f"An unexpected error occurred: {err}")


def get_eth_transaction_details(
    *,
    session: Session,
    tx_hashes: Optional[List[str]] = None,
    limit: int = 50,
    skip: int = 0,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> TransactionsPublic:
    """
    Retrieves and displays details of eth transactions, accepts filtering by tx_hash.
    """
    if not web3.is_connected():
        raise ConnectionError("Failed to connect to the Ethereum node.")

    # Fetch all transactions from DB if no filters are provided
    if not tx_hashes:
        transactions = get_transactions(session=session, skip=skip, limit=limit, start_time=start_time, end_time=end_time)
        return transactions

    # If tx_hashes are given, search DB, fetch and insert  missing transactions if any
    transactions = get_transactions(session=session, tx_hashes=tx_hashes)
    found_tx_hashes = {tx.tx_hash for tx in transactions.data}
    missing_tx_hashes = set(tx_hashes) - found_tx_hashes

    if missing_tx_hashes:
        new_transactions = []
        for tx_hash in missing_tx_hashes:
            try:
                new_transaction = get_eth_transaction_detail_for_insert(session=session, tx_hash=tx_hash)
                new_transactions.append(new_transaction)
            except Exception as e:
                print(f"Error fetching transaction {tx_hash}: {e}")

        if new_transactions:
            insert_transactions(session=session, transactions_create=new_transactions)

    # Fetch and return filtered results
    transactions = get_transactions(session=session, tx_hashes=tx_hashes, start_time=start_time, end_time=end_time, skip=skip, limit=limit)
    return transactions
