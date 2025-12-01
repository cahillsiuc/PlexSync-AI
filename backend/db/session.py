"""
Database Session Management
Clean session handling with dependency injection
"""
from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
from config import settings

# Import all models to register them with SQLModel metadata
from models import (
    BaseModel,
    VendorInvoice,
    PlexInvoice,
    PurchaseOrder,
    SyncOperation,
    User,
    AuditLog
)

# Create engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_pre_ping=True,  # Verify connections before using
)

def create_db_and_tables():
    """Create all tables"""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI routes
    Usage: session: Session = Depends(get_session)
    """
    with Session(engine) as session:
        yield session

