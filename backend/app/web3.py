from web3 import Web3
from web3.exceptions import TransactionNotFound, BlockNotFound
from app.core.config import settings
from datetime import datetime
from typing import Any

web3 = Web3(Web3.HTTPProvider(settings.INFURA_HTTPS))

def get_eth_transaction_details(*, tx_hash: str) -> Any:
    """
    Retrieves and displays details for a given Ethereum transaction hash.
    """
    if not web3.is_connected():
        raise ConnectionError("Failed to connect to the Ethereum node.")
    
    try:
        print("entered get eth transaction")
        tx = web3.eth.get_transaction(tx_hash)
        tx_receipt = web3.eth.get_transaction_receipt(tx_hash)
        block = web3.eth.get_block(tx['blockNumber'])
        timestamp = block['timestamp']

        gas_price_gwei = web3.from_wei(tx['gasPrice'], 'gwei')
        gas_used = tx_receipt['gasUsed']
        total_gas_cost_eth = web3.from_wei(tx['gasPrice'] * gas_used, 'ether')

        eth_price_usd = 3138.01000000
        total_gas_cost_usd = float(total_gas_cost_eth) * eth_price_usd

        datetime_converted = datetime.utcfromtimestamp(timestamp)

        transaction_details = {
            "Transaction Hash": tx.hash.hex(),
            "Block Number": tx.blockNumber,
            "Timestamp": datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') + ' UTC',
            "Timestamp_ms": int(datetime_converted.timestamp()*1000),
            "From": tx['from'],
            "To": tx['to'],
            "Value": f"{web3.from_wei(tx['value'], 'ether')} ETH",
            "Gas Price": f"{gas_price_gwei} Gwei",
            "Gas Used": gas_used,
            "Total Gas Cost": f"{total_gas_cost_eth} ETH",
            "Historical ETH Price": f"${eth_price_usd:.2f} USD",
            "Total Gas Cost in USD": f"${total_gas_cost_usd:.2f}",
            "Status": 'Success' if tx_receipt.status == 1 else 'Failure'
        }

        return transaction_details

    except TransactionNotFound:
        print("entered txn not found")
        raise ValueError(f"Transaction with hash {tx_hash} not found.")
    except BlockNotFound:
        print("entered block not found")
        raise ValueError(f"Block containing transaction {tx_hash} not found.")
    except RuntimeError as re:
        raise re
    except Exception as err:
        raise RuntimeError(f"An unexpected error occurred: {err}")
