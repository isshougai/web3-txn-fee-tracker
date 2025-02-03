import uuid

from datetime import datetime
from sqlmodel import Field, SQLModel, UniqueConstraint

# Shared properties
class TransactionBase(SQLModel):
    """Base model for Ethereum transaction."""
    tx_hash: str = Field(unique=True, index=True, max_length=66)
    timestamp: datetime = Field(index=True)
    txn_fee_usdt: float
    gas_used: int
    gas_price_wei: int
    txn_fee_eth: float
    eth_usdt_price: float

class TransactionCreate(TransactionBase):
    """Create model for Ethereum transaction."""
    pass

# Database model, database table inferred from class name
class Transaction(TransactionBase, table=True):
    """Database model for Ethereum transaction."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

# Properties to return via API, id is always required
class TransactionPublic(TransactionBase):
    """Transaction response model for return via API."""
    id: uuid.UUID

class TransactionsPublic(SQLModel):
    """Transactions response model for return via API."""
    data: list[TransactionPublic]
    count: int


# Shared properties
class LastUpdateBase(SQLModel):
    """Base model for data last update."""
    type: str = Field(unique=True, index=True, max_length=50)
    timestamp: datetime

class LastUpdateCreate(LastUpdateBase):
    """Base model for data last update."""
    pass

# Database model, database table inferred from class name
class LastUpdate(LastUpdateBase, table=True):
    """Database model for data last update."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

# Shared properties
class SpotPriceBase(SQLModel):
    """Base model for spot price data."""
    symbol: str = Field(index=True, max_length=10)
    timestamp: datetime = Field(index=True)
    price: float

class SpotPriceCreate(SpotPriceBase):
    """Base model for spot price data."""
    pass

# Database model, database table inferred from class name
class SpotPrice(SpotPriceBase, table=True):
    """Database model for spot price data."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    __table_args__ = (
        UniqueConstraint("symbol", "timestamp", name="symbol_timestamp_uc"),
    )
