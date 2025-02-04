from typing import Any, List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from app.api.deps import HttpClientDep, SessionDep
from app import web3, crud
from app.models import TransactionsPublic
from datetime import datetime, timezone


router = APIRouter(prefix="/transactions", tags=["transaction"])

@router.get(
    "/",
    response_model=TransactionsPublic,
)
def get_transactions(
    session: SessionDep,
    client: HttpClientDep, 
    tx_hashes: Optional[List[str]] = Query(None),
    start_time: Optional[int] = Query(None),
    end_time: Optional[int] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
) -> Any:
    """
    Get transactions based on optional tx_hashes and optional date range.
    Supports pagination with skip and limit parameters.
    """
    try:
        start_time = datetime.fromtimestamp(start_time / 1000, tz=timezone.utc) if start_time else None
        end_time = datetime.fromtimestamp(end_time / 1000, tz=timezone.utc) if end_time else None

        transactions = web3.get_eth_transaction_details(session=session, client=client, tx_hashes=tx_hashes, start_time=start_time, end_time=end_time, skip=skip, limit=limit)

        return transactions
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction(s) not found."
        )
    except RuntimeError as re:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(re)
        )
    except ConnectionError as re:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(re)
        )
