from sqlmodel import Session, create_engine
from app.core.config import settings
from app.models import LastUpdateCreate
from app import crud

from datetime import datetime, timedelta, timezone

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28
def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)
    init_lastupdate_timestamp = datetime.now(timezone.utc) - timedelta(minutes=5)

    lastupdate_transaction = crud.get_lastupdate_transaction(session=session)
    if not lastupdate_transaction:
        lastupdate_transaction = LastUpdateCreate(type="transaction", timestamp=init_lastupdate_timestamp)
        crud.insert_lastupdate_transaction(session=session, lastupdate_transaction_insert=lastupdate_transaction)

    lastupdate_spot_price = crud.get_lastupdate_spot_price(session=session)
    if not lastupdate_spot_price:
        lastupdate_spot_price = LastUpdateCreate(type="spot_price", timestamp=init_lastupdate_timestamp)
        crud.insert_lastupdate_spot_price(session=session, lastupdate_spot_price_insert=lastupdate_spot_price)