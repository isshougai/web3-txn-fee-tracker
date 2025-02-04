from typing import Any
from fastapi import APIRouter, HTTPException

from app.api.deps import HttpClientDep
from app import binance
from app.models import SpotPricePublic


router = APIRouter(prefix="/prices", tags=["prices"])

@router.get(
    "/{symbol}",
    response_model=SpotPricePublic,
)
def get_prices(symbol: str) -> Any:
    """
    Returns the latest spot price for a given symbol
    """
    try:
        response = binance.get_ticker_current_price(symbol=symbol.upper())
        if response is None:
            raise HTTPException(status_code=404, detail="Price not found")
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

