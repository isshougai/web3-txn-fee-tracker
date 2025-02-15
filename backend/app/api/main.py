from fastapi import APIRouter

from app.api.routes import prices, transaction, utils

api_router = APIRouter()
api_router.include_router(prices.router)
api_router.include_router(transaction.router)
api_router.include_router(utils.router)
