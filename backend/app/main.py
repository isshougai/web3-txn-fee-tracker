from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.routing import APIRoute
import httpx
import schedule
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.api.deps import get_db
from app.core.config import settings
from app.tasks import long_running_task, run_continuously


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = httpx.Client(timeout=10.0)
    app.state.client = client

    long_running_task(client=client)
    stop_run_continuously = run_continuously()
    schedule.every(settings.SCHEDULER_INTERVAL_MINUTES).minute.do(long_running_task, client=client)
    app.state.stop_run_continuously = stop_run_continuously

    yield 

    if stop_run_continuously:
        stop_run_continuously.set()
    client.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
