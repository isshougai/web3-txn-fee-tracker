from sqlmodel import Session, select, func
from datetime import datetime
from typing import Dict, Optional, List
from app.models import Transaction, TransactionCreate, TransactionsPublic, LastUpdate, LastUpdateCreate, SpotPrice, SpotPriceCreate
from sqlalchemy.exc import IntegrityError


# CRUD for Transaction
def get_transactions(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 50,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    tx_hashes: Optional[List[str]] = None
) -> TransactionsPublic:
    base_statement = select(Transaction)
    
    if start_time:
        base_statement = base_statement.where(Transaction.timestamp >= start_time)
    if end_time:
        base_statement = base_statement.where(Transaction.timestamp <= end_time)
    if tx_hashes:
        base_statement = base_statement.where(Transaction.tx_hash.in_(tx_hashes))
    
    count_statement = select(func.count()).select_from(base_statement.subquery())
    count = session.exec(count_statement).one()

    statement = base_statement.order_by(Transaction.timestamp.desc()).offset(skip).limit(limit)
    
    db_objs = session.exec(statement).all()
    return TransactionsPublic(data=db_objs, count=count)

def insert_transactions(*, session: Session, transactions_create: List[TransactionCreate]) -> List[Transaction]:
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

def get_spot_prices(
    *,
    session: Session,
    symbol: str,
    timestamps: List[datetime]
) -> List[SpotPrice]:
    statement = select(SpotPrice).where(
        SpotPrice.symbol == symbol,
        SpotPrice.timestamp.in_(timestamps)
    )
    db_objs = session.exec(statement).all()
    return db_objs

def insert_spot_prices(*, session: Session, spot_prices_create: List[SpotPriceCreate]) -> List[SpotPrice]:
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
def get_lastupdate_transaction(*, session: Session) -> Optional[LastUpdate]:
    statement = select(LastUpdate).where(LastUpdate.type == "transaction")
    db_obj = session.exec(statement).first()
    return db_obj

def get_lastupdate_spot_price(*, session: Session) -> Optional[LastUpdate]:
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

def update_lastupdate_transaction(*, session: Session, end_time: datetime) -> Optional[LastUpdate]:
    statement = select(LastUpdate).where(LastUpdate.type == "transaction")
    db_obj = session.exec(statement).first()
    if db_obj:
        db_obj.timestamp = end_time
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    return db_obj

def update_lastupdate_spot_price(*, session: Session, end_time: datetime) -> Optional[LastUpdate]:
    statement = select(LastUpdate).where(LastUpdate.type == "spot_price")
    db_obj = session.exec(statement).first()
    if db_obj:
        db_obj.timestamp = end_time
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    return db_obj

