from typing import Any
from fastapi import APIRouter, HTTPException, status
from app.api.deps import HttpClientDep
from app import web3


router = APIRouter(prefix="/transaction", tags=["transaction"])

@router.get(
    "/",

)
def get_transactions(client: HttpClientDep, tx_hash: str) -> Any:
    """
    Test function.
    """
    try:
        response = web3.get_eth_transaction_details(tx_hash=tx_hash)
        return response
    except ValueError:
        # Raised when the transaction with the given hash is not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with hash {tx_hash} not found."
        )
    except RuntimeError as re:
        # Handle RuntimeError exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(re)
        )
