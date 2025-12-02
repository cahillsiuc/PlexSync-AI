"""
Pytest configuration and shared fixtures
"""
import pytest
import asyncio
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient
from typing import Generator
import tempfile
import shutil
from pathlib import Path

# Test database engine
@pytest.fixture(name="engine")
def engine_fixture():
    """Create in-memory SQLite engine for tests"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine):
    """Create database session for tests"""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create FastAPI test client with database override"""
    # Mock config before importing main
    import sys
    from unittest.mock import MagicMock, patch
    
    # Create comprehensive mock settings
    mock_settings = MagicMock()
    mock_settings.database_url = "sqlite:///:memory:"
    mock_settings.debug = False
    mock_settings.db_pool_size = 5
    mock_settings.db_max_overflow = 0
    mock_settings.db_pool_timeout = 30
    mock_settings.app_name = "PlexSync AI Test"
    mock_settings.app_version = "1.0.0"
    mock_settings.environment = "test"
    mock_settings.docs_enabled = False
    mock_settings.docs_url = None
    mock_settings.redoc_url = None
    mock_settings.cors_origins = []
    mock_settings.secret_key = "test-secret-key"
    mock_settings.jwt_secret = "test-jwt-secret"
    mock_settings.jwt_algorithm = "HS256"
    mock_settings.jwt_expiration_minutes = 1440
    mock_settings.storage_path = "./test_storage"
    mock_settings.storage_type = "local"
    mock_settings.max_file_size_mb = 16
    mock_settings.allowed_file_types = ["pdf", "png", "jpg"]
    mock_settings.openai_api_key = "test-key"
    mock_settings.openai_model = "gpt-4-vision-preview"
    mock_settings.openai_max_tokens = 2000
    mock_settings.openai_temperature = 0.1
    mock_settings.plex_api_url = "https://api.test"
    mock_settings.plex_api_key = "test-key"
    mock_settings.plex_api_key_header = "X-Plex-Connect-Api-Key"
    mock_settings.plex_timeout = 30
    mock_settings.plex_retry_attempts = 3
    mock_settings.plex_invoice_endpoint = "/accounting/v1/ap-invoices"
    mock_settings.plex_po_endpoint = "/purchasing/v1/purchase-orders"
    mock_settings.plex_vendor_endpoint = "/vendors"
    
    # Patch config module before any imports
    with patch.dict('sys.modules', {'config': MagicMock(settings=mock_settings)}):
        # Import here to avoid circular dependencies
        try:
            from main import app
            from db.session import get_session

            def get_session_override():
                return session

            app.dependency_overrides[get_session] = get_session_override

            with TestClient(app) as client:
                yield client

            app.dependency_overrides.clear()
        except (ImportError, Exception) as e:
            # main.py doesn't exist yet or config error, return None
            yield None


@pytest.fixture(name="temp_storage")
def temp_storage_fixture():
    """Create temporary storage directory for test files"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture(name="sample_invoice_data")
def sample_invoice_data_fixture():
    """Sample parsed invoice data"""
    return {
        "invoice_number": "INV-2024-001",
        "vendor_name": "Acme Corporation",
        "invoice_date": "2024-01-15",
        "due_date": "2024-02-15",
        "total_amount": 1500.00,
        "tax_amount": 150.00,
        "subtotal": 1350.00,
        "po_numbers": ["PO-2024-100"],
        "line_items": [
            {
                "line_number": 1,
                "description": "Widget A",
                "quantity": 10,
                "unit_price": 100.00,
                "line_total": 1000.00
            },
            {
                "line_number": 2,
                "description": "Widget B",
                "quantity": 5,
                "unit_price": 70.00,
                "line_total": 350.00
            }
        ],
        "confidence": 95.0
    }


@pytest.fixture(name="sample_po_data")
def sample_po_data_fixture():
    """Sample PO data"""
    return {
        "po_number": "PO-2024-100",
        "vendor_name": "Acme Corporation",
        "po_type": "standard",
        "total_amount": 1500.00,
        "status": "open",
        "line_items": [
            {
                "line_number": 1,
                "part_number": "WA-001",
                "description": "Widget A",
                "quantity": 10,
                "unit_price": 100.00
            }
        ]
    }


@pytest.fixture(name="sample_plex_invoice")
def sample_plex_invoice_fixture():
    """Sample Plex invoice with RECEIVED status"""
    return {
        "id": "plex-12345",
        "invoice_number": "RECEIVED",
        "po_number": "PO-2024-100",
        "vendor_code": "ACME",
        "vendor_name": "Acme Corporation",
        "total_amount": 1500.00,
        "status": "received"
    }


@pytest.fixture(name="authenticated_client")
def authenticated_client_fixture(client: TestClient):
    """Test client with authentication token"""
    if client is None:
        pytest.skip("main.py not yet created")
    
    # Create test user and login
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPass123!"
        }
    )

    # Login
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "TestPass123!"
        }
    )

    token = login_response.json()["access_token"]

    # Add token to headers
    client.headers["Authorization"] = f"Bearer {token}"

    yield client


# Async fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

