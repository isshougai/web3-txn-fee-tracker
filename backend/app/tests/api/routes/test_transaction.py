from uuid import uuid4
import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from unittest.mock import patch

from sqlmodel import Session

from app.main import app
from app.core.config import settings
from app.models import TransactionsPublic, TransactionPublic
from app.api.deps import HttpClientDep, SessionDep

client = TestClient(app)

@pytest.fixture
def db_session():
    from app.core.db import get_session
    session = next(get_session())  # Manually create a session
    yield session
    session.close()

@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_client(test_client):
    with patch("app.api.deps.HttpClientDep", return_value=test_client):
        with patch("app.api.deps.get_client_from_request", return_value=test_client):
            yield test_client

def test_get_transactions_success(db_session: Session, mock_client) -> None:
    tx_hash = "0x123"
    timestamp = datetime.now(tz=timezone.utc)
    mock_transaction = TransactionPublic(
        id=uuid4(),
        tx_hash=tx_hash,
        timestamp=timestamp.isoformat(),
        txn_fee_usdt=10.0,
        gas_used=21000,
        gas_price_wei=1000000000,
        txn_fee_eth=0.01,
        eth_usdt_price=1000.0
    )
    mock_response = TransactionsPublic(data=[mock_transaction], count=1)

    with patch("app.web3.get_eth_transaction_details", return_value=mock_response):
        response = mock_client.get(f"{settings.API_V1_STR}/transactions/")
        assert response.status_code == 200
        transactions = response.json()
        assert len(transactions["data"]) > 0
        assert transactions["count"] == 1
        assert transactions["data"][0]["tx_hash"] == tx_hash

def test_get_transactions_with_filters(db_session: Session, mock_client) -> None:
    tx_hash = "0x123"
    timestamp = datetime.now(tz=timezone.utc)
    mock_transaction = TransactionPublic(
        id=uuid4(),
        tx_hash=tx_hash,
        timestamp=timestamp.isoformat(),
        txn_fee_usdt=10.0,
        gas_used=21000,
        gas_price_wei=1000000000,
        txn_fee_eth=0.01,
        eth_usdt_price=1000.0
    )
    mock_response = TransactionsPublic(data=[mock_transaction], count=1)

    start_time = int((timestamp - timedelta(minutes=1)).timestamp() * 1000)
    end_time = int((timestamp + timedelta(minutes=1)).timestamp() * 1000)

    with patch("app.web3.get_eth_transaction_details", return_value=mock_response):
        response = mock_client.get(f"{settings.API_V1_STR}/transactions/", params={
            "start_time": start_time,
            "end_time": end_time,
            "tx_hashes": [tx_hash]
        })
        assert response.status_code == 200
        transactions = response.json()
        assert len(transactions["data"]) == 1
        assert transactions["data"][0]["tx_hash"] == tx_hash

def test_get_transactions_not_found(db_session: Session, mock_client) -> None:
    with patch("app.web3.get_eth_transaction_details", side_effect=ValueError("Transaction(s) not found.")):
        response = mock_client.get(f"{settings.API_V1_STR}/transactions/", params={
            "tx_hashes": ["non_existing_tx_hash"]
        })
        assert response.status_code == 404
        assert response.json()["detail"] == "Transaction(s) not found."

def test_get_transactions_internal_server_error(db_session: Session, mock_client) -> None:
    with patch("app.web3.get_eth_transaction_details", side_effect=RuntimeError("Internal Server Error")):
        response = mock_client.get(f"{settings.API_V1_STR}/transactions/")
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal Server Error"

def test_get_transactions_connection_error(db_session: Session, mock_client) -> None:
    with patch("app.web3.get_eth_transaction_details", side_effect=ConnectionError("Connection Error")):
        response = mock_client.get(f"{settings.API_V1_STR}/transactions/")
        assert response.status_code == 500
        assert response.json()["detail"] == "Connection Error"