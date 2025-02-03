from fastapi import APIRouter

from app.api.routes import prices, transaction

api_router = APIRouter()
api_router.include_router(prices.router)
api_router.include_router(transaction.router)
