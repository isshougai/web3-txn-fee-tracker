from uuid import uuid4
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from sqlmodel import Session

from app.crud import (
    get_transactions,
    insert_transactions,
    get_spot_price,
    get_spot_prices,
    insert_spot_prices
)
from app.models import Transaction, TransactionCreate, SpotPrice, SpotPriceCreate, TransactionsPublic

@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)

def test_get_transactions(mock_session):
    start_time = datetime.now(tz=timezone.utc)
    end_time = datetime.now(tz=timezone.utc)
    tx_hashes = ["0x123"]
    skip = 0
    limit = 10

    mock_transaction = Transaction(
        id=uuid4(),
        tx_hash="0x123",
        timestamp=start_time,
        txn_fee_usdt=10.0,
        gas_used=21000,
        gas_price_wei=1000000000,
        txn_fee_eth=0.01,
        eth_usdt_price=1000.0
    )
    mock_session.exec.return_value.all.return_value = [mock_transaction]
    mock_session.exec.return_value.one.return_value = 1

    result = get_transactions(
        session=mock_session,
        start_time=start_time,
        end_time=end_time,
        tx_hashes=tx_hashes,
        skip=skip,
        limit=limit
    )

    assert isinstance(result, TransactionsPublic)
    assert len(result.data) == 1
    assert result.count == 1
    assert result.data[0].tx_hash == "0x123"

def test_insert_transactions(mock_session):
    transactions_create = [
        TransactionCreate(
            tx_hash="0x123",
            timestamp=datetime.now(tz=timezone.utc),
            txn_fee_usdt=10.0,
            gas_used=21000,
            gas_price_wei=1000000000,
            txn_fee_eth=0.01,
            eth_usdt_price=1000.0
        )
    ]

    mock_transaction = Transaction(
        id=1,
        tx_hash="0x123",
        timestamp=datetime.now(tz=timezone.utc),
        txn_fee_usdt=10.0,
        gas_used=21000,
        gas_price_wei=1000000000,
        txn_fee_eth=0.01,
        eth_usdt_price=1000.0
    )
    mock_session.exec.return_value = None
    mock_session.commit.return_value = None
    mock_session.rollback.return_value = None

    with patch("app.crud.Transaction.model_validate", return_value=mock_transaction):
        result = insert_transactions(session=mock_session, transactions_create=transactions_create)

    assert len(result) == 1
    assert result[0].tx_hash == "0x123"

def test_get_spot_price(mock_session):
    symbol = "ETH"
    timestamp = datetime.now(tz=timezone.utc)

    mock_spot_price = SpotPrice(
        id=1,
        symbol=symbol,
        timestamp=timestamp,
        price=1000.0
    )
    mock_session.exec.return_value.first.return_value = mock_spot_price

    result = get_spot_price(session=mock_session, symbol=symbol, timestamp=timestamp)

    assert result is not None
    assert result.symbol == "ETH"
    assert result.price == 1000.0

def test_get_spot_prices(mock_session):
    symbol = "ETH"
    timestamps = [datetime.now(tz=timezone.utc)]

    mock_spot_price = SpotPrice(
        id=1,
        symbol=symbol,
        timestamp=timestamps[0],
        price=1000.0
    )
    mock_session.exec.return_value.all.return_value = [mock_spot_price]

    result = get_spot_prices(session=mock_session, symbol=symbol, timestamps=timestamps)

    assert len(result) == 1
    assert result[0].symbol == "ETH"
    assert result[0].price == 1000.0

def test_insert_spot_prices(mock_session):
    spot_prices_create = [
        SpotPriceCreate(
            symbol="ETH",
            timestamp=datetime.now(tz=timezone.utc),
            price=1000.0
        )
    ]

    mock_spot_price = SpotPrice(
        id=1,
        symbol="ETH",
        timestamp=datetime.now(tz=timezone.utc),
        price=1000.0
    )
    mock_session.exec.return_value = None
    mock_session.commit.return_value = None
    mock_session.rollback.return_value = None

    with patch("app.crud.SpotPrice.model_validate", return_value=mock_spot_price):
        result = insert_spot_prices(session=mock_session, spot_prices_create=spot_prices_create)

    assert len(result) == 1
    assert result[0].symbol == "ETH"
    assert result[0].price == 1000.0