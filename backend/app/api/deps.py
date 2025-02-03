from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, Request
from sqlmodel import Session

from app.core.db import engine
import httpx


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]


def get_client_from_request(request: Request) -> httpx.Client:
    return request.state.client

HttpClientDep = Annotated[httpx.Client, Depends(get_client_from_request)]