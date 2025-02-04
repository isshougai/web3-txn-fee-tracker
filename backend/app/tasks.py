import httpx
import schedule
import time
import threading
from datetime import datetime, timedelta, timezone
from sqlmodel import Session
from app import binance, etherscan, crud
from app.core.db import engine
from app.core.config import settings

def long_running_task(client: httpx.Client):
    with Session(engine) as session:
        end_time = datetime.now(tz=timezone.utc)
        print("Running long running task, current time:", end_time, " UTC")
        update_price_and_transactions(session=session, client=client, end_time=end_time)

def update_price_and_transactions(session: Session, client: httpx.Client, end_time: datetime):
    last_update_spot_price = crud.get_lastupdate_spot_price(session=session)
    spot_price_update_start_time = last_update_spot_price.timestamp + timedelta(seconds=1) if last_update_spot_price else end_time - timedelta(minutes=5)

    binance.batch_save_ethusdt_price(session=session, start_time=spot_price_update_start_time, end_time=end_time)
    crud.update_lastupdate_spot_price(session=session, end_time=end_time)

    last_update_transaction = crud.get_lastupdate_transaction(session=session)
    transaction_update_start_time = last_update_transaction.timestamp + timedelta(seconds=1) if last_update_transaction else end_time - timedelta(minutes=5)

    starting_block = etherscan.get_block_no_by_timestamp(client=client, timestamp=int(transaction_update_start_time.timestamp()))
    ending_block = etherscan.get_block_no_by_timestamp(client=client, timestamp=int(end_time.timestamp()))

    transactions = etherscan.get_erc20_token_transfer_events(
            client=client,
            session=session,
            address=settings.UNISWAP_V3_ETH_USDC_ADDRESS,
            from_block=starting_block,
            to_block=ending_block
        )

    crud.insert_transactions(session=session, transactions_create=transactions)
    crud.update_lastupdate_transaction(session=session, end_time=end_time)


def run_continuously(interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run
