from typing import Any
from fastapi import APIRouter

from app.api.deps import HttpClientDep
from app import binance


router = APIRouter(prefix="/prices", tags=["prices"])

@router.get(
    "/",
)
def get_prices(client: HttpClientDep) -> Any:
    """
    Test function.
    """

    binance.get_ethusdt_price()

    return

