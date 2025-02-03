from sqlmodel import Session, select, func
from datetime import datetime
from typing import Optional
from app.models import Transaction, TransactionCreate, TransactionsPublic, LastUpdate, LastUpdateCreate, SpotPrice, SpotPriceCreate
from sqlalchemy.exc import IntegrityError


# CRUD for Transaction
def get_transactions(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 50,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    tx_hashes: Optional[list[str]] = None
) -> TransactionsPublic:
    count_statement = select(func.count()).select_from(Transaction)
    count = session.exec(count_statement).one()

    statement = select(Transaction).offset(skip).limit(limit)
    
    if start_date:
        statement = statement.where(Transaction.timestamp >= start_date)
    if end_date:
        statement = statement.where(Transaction.timestamp <= end_date)
    if tx_hashes:
        statement = statement.where(Transaction.tx_hash.in_(tx_hashes))
    
    db_objs = session.exec(statement).all()
    return TransactionsPublic(data=db_objs, count=count)

def insert_transactions(*, session: Session, transactions_create: list[TransactionCreate]) -> list[Transaction]:
    db_objs = []
    for tx in transactions_create:
        db_obj = Transaction.model_validate(tx)
        session.add(db_obj)
        try:
            session.commit()
            session.refresh(db_obj)
            db_objs.append(db_obj)
        except IntegrityError:
            session.rollback()
            print(f"Duplicate entry found for transaction: {tx}")
    return db_objs


# CRUD for SpotPrice
def get_spot_price(
    *,
    session: Session,
    symbol: str,
    timestamp: datetime
) -> SpotPrice | None:
    statement = select(SpotPrice).where(SpotPrice.symbol == symbol).where(SpotPrice.timestamp == timestamp)
    db_obj = session.exec(statement).first()
    return db_obj

def insert_spot_prices(*, session: Session, spot_prices_create: list[SpotPriceCreate]) -> list[SpotPrice]:
    db_objs = []
    for sp in spot_prices_create:
        db_obj = SpotPrice.model_validate(sp)
        session.add(db_obj)
        try:
            session.commit()
            session.refresh(db_obj)
            db_objs.append(db_obj)
        except IntegrityError:
            session.rollback()
            print(f"Duplicate entry found for spot price: {sp}")
    return db_objs

# CRUD for LastUpdate
def get_lastupdate_transaction(*, session: Session) -> LastUpdate | None:
    statement = select(LastUpdate).where(LastUpdate.type == "transaction")
    db_obj = session.exec(statement).first()
    return db_obj

def get_lastupdate_spot_price(*, session: Session) -> LastUpdate | None:
    statement = select(LastUpdate).where(LastUpdate.type == "spot_price")
    db_obj = session.exec(statement).first()
    return db_obj

def insert_lastupdate_transaction(*, session: Session, lastupdate_transaction_insert: LastUpdateCreate) -> LastUpdate:
    db_obj = LastUpdate.model_validate(
        lastupdate_transaction_insert
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def insert_lastupdate_spot_price(*, session: Session, lastupdate_spot_price_insert: LastUpdateCreate) -> LastUpdate:
    db_obj = LastUpdate.model_validate(
        lastupdate_spot_price_insert
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def update_lastupdate_transaction(*, session: Session) -> LastUpdate | None:
    statement = select(LastUpdate).where(LastUpdate.type == "transaction")
    db_obj = session.exec(statement).first()
    if db_obj:
        db_obj.timestamp = datetime.now()
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    return db_obj

def update_lastupdate_spot_price(*, session: Session) -> LastUpdate | None:
    statement = select(LastUpdate).where(LastUpdate.type == "spot_price")
    db_obj = session.exec(statement).first()
    if db_obj:
        db_obj.timestamp = datetime.now()
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    return db_obj

