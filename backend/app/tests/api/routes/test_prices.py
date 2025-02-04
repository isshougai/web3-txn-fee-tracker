from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.core.config import settings
from app.models import SpotPricePublic

client = TestClient(app)

def test_get_prices_success():
    symbol = "ETHUSDT"
    mock_response = SpotPricePublic(symbol=symbol, timestamp="2025-02-04T08:37:22.801Z", price=3000.0)

    with patch("app.binance.get_ticker_current_price", return_value=mock_response):
        response = client.get(f"{settings.API_V1_STR}/prices/{symbol}")
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == symbol
        assert data["price"] == 3000.0

def test_get_prices_not_found():
    symbol = "INVALID"
    
    with patch("app.binance.get_ticker_current_price", return_value=None):
        response = client.get(f"{settings.API_V1_STR}/prices/{symbol}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Price not found"

def test_get_prices_internal_server_error():
    symbol = "ETHUSDT"
    
    with patch("app.binance.get_ticker_current_price", side_effect=Exception("Internal Server Error")):
        response = client.get(f"{settings.API_V1_STR}/prices/{symbol}")
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal Server Error"