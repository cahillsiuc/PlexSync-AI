# PlexSync AI - Complete Build Guide for Cursor

**Foundation Status:** ✅ Complete
**Next Phase:** Backend Core + Frontend + Tests
**Estimated Time:** 8-10 hours

---

## 📋 BUILD CHECKLIST

### ✅ Already Done (By Claude Code)
- [x] Project structure
- [x] README.md
- [x] LICENSE
- [x] .env.example
- [x] docker-compose.yml
- [x] backend/requirements.txt
- [x] backend/Dockerfile
- [x] backend/config.py
- [x] .gitignore

### 🔄 Phase 2: Database Models & Core (2 hours)
- [ ] `backend/models/__init__.py`
- [ ] `backend/models/base.py`
- [ ] `backend/models/vendor_invoice.py`
- [ ] `backend/models/purchase_order.py`
- [ ] `backend/models/plex_invoice.py`
- [ ] `backend/models/sync_operation.py`
- [ ] `backend/models/user.py`
- [ ] `backend/models/audit_log.py`
- [ ] `backend/db/session.py`
- [ ] `backend/db/__init__.py`

### 🔄 Phase 3: Core Services (2 hours)
- [ ] `backend/core/__init__.py`
- [ ] `backend/core/plex_client.py` ⭐ CRITICAL
- [ ] `backend/core/ai_parser.py` ⭐ CRITICAL
- [ ] `backend/core/matcher.py`
- [ ] `backend/core/learning.py`
- [ ] `backend/services/email_service.py`
- [ ] `backend/services/storage_service.py`
- [ ] `backend/services/notification_service.py`

### 🔄 Phase 4: API Endpoints (2 hours)
- [ ] `backend/main.py` ⭐ CRITICAL
- [ ] `backend/api/__init__.py`
- [ ] `backend/api/auth.py`
- [ ] `backend/api/invoices.py` ⭐ CRITICAL
- [ ] `backend/api/sync.py` ⭐ CRITICAL
- [ ] `backend/api/analytics.py`
- [ ] `backend/api/webhooks.py`

### 🔄 Phase 5: Tests (2 hours)
- [ ] `backend/tests/conftest.py`
- [ ] `backend/tests/test_models.py`
- [ ] `backend/tests/test_plex_client.py`
- [ ] `backend/tests/test_ai_parser.py`
- [ ] `backend/tests/test_api_invoices.py`
- [ ] `backend/tests/test_api_sync.py`
- [ ] `backend/tests/test_integration.py`

### 🔄 Phase 6: Frontend (3 hours)
- [ ] `frontend/package.json`
- [ ] `frontend/vite.config.ts`
- [ ] `frontend/tsconfig.json`
- [ ] `frontend/src/main.tsx`
- [ ] `frontend/src/App.tsx`
- [ ] `frontend/src/pages/Dashboard.tsx`
- [ ] `frontend/src/pages/Upload.tsx`
- [ ] `frontend/src/pages/Review.tsx`
- [ ] `frontend/src/components/ui/*` (shadcn/ui)
- [ ] `frontend/src/api/client.ts`

---

## 🏗️ DETAILED BUILD INSTRUCTIONS

### **PHASE 2: DATABASE MODELS**

#### **File 1: `backend/models/base.py`**
```python
"""
Base model with common fields for all models
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

class BaseModel(SQLModel):
    """Base model with common fields"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
```

#### **File 2: `backend/models/vendor_invoice.py`**
```python
"""
Vendor Invoice Model - Stores invoices received from vendors
"""
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict, Any, List
from datetime import date
from .base import BaseModel

class VendorInvoice(BaseModel, table=True):
    """Invoice received from vendor (email or upload)"""
    __tablename__ = "vendor_invoices"

    # Basic Info
    invoice_number: str = Field(index=True)
    vendor_name: str = Field(index=True)

    # Dates
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None

    # Amounts
    total_amount: Optional[float] = None
    tax_amount: Optional[float] = None
    subtotal: Optional[float] = None

    # PO References
    po_numbers: List[str] = Field(default=[], sa_column=Column(JSON))

    # File Storage
    file_path: str  # Path to original PDF/image
    file_type: str  # pdf, png, jpg, etc.
    file_size: int  # bytes

    # AI Parsing Results
    raw_text: Optional[str] = None
    parsed_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    confidence_score: float = 0.0

    # Line Items (JSON array)
    line_items: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))

    # Status
    status: str = Field(default="received")  # received, parsed, matched, synced, failed

    # Email Source (if from email)
    email_message_id: Optional[str] = Field(default=None, index=True)
    email_from: Optional[str] = None
    email_subject: Optional[str] = None

    # Metadata
    metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
```

#### **File 3: `backend/models/plex_invoice.py`**
```python
"""
Plex Invoice Model - Represents invoices in Plex ERP
"""
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict, Any
from datetime import date
from .base import BaseModel

class PlexInvoice(BaseModel, table=True):
    """Invoice from Plex ERP system"""
    __tablename__ = "plex_invoices"

    # Plex IDs
    plex_invoice_id: str = Field(unique=True, index=True)
    invoice_number: str = Field(index=True)  # Could be "RECEIVED" initially

    # PO Reference
    po_number: str = Field(index=True)

    # Vendor
    vendor_code: Optional[str] = None
    vendor_name: Optional[str] = None

    # Amounts
    total_amount: Optional[float] = None

    # Status
    status: str = Field(default="received")  # received, posted, paid

    # Dates
    invoice_date: Optional[date] = None
    received_date: Optional[date] = None
    posted_date: Optional[date] = None

    # Raw Plex data (for reference)
    plex_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Sync tracking
    last_synced_at: Optional[datetime] = None
    sync_status: str = "pending"  # pending, synced, failed
```

#### **File 4: `backend/models/sync_operation.py`**
```python
"""
Sync Operation Model - Tracks invoice sync operations for learning
"""
from sqlmodel import SQLModel, Field, Column, JSON, Relationship
from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseModel

class SyncOperation(BaseModel, table=True):
    """Tracks sync operations between vendor invoice and Plex"""
    __tablename__ = "sync_operations"

    # References
    vendor_invoice_id: int = Field(foreign_key="vendor_invoices.id", index=True)
    plex_invoice_id: int = Field(foreign_key="plex_invoices.id", index=True)

    # Operation Details
    operation_type: str  # update_invoice_number, create_invoice, update_line_items

    # Before/After for learning
    before_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    after_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Confidence & Success
    confidence_before: float = 0.0
    confidence_after: float = 0.0
    success: bool = False

    # User Corrections (for ML learning)
    user_corrections: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    correction_count: int = 0

    # Timing
    processing_time_ms: int = 0

    # Error tracking
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    retry_count: int = 0

    # Learning data
    po_type: Optional[str] = None  # For scenario-specific learning
    vendor_pattern: Optional[str] = None

    # User who performed sync
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
```

#### **File 5: `backend/models/purchase_order.py`**
```python
"""
Purchase Order Model - Stores PO data from Plex
"""
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict, Any, List
from datetime import date
from .base import BaseModel

class PurchaseOrder(BaseModel, table=True):
    """Purchase Order from Plex ERP"""
    __tablename__ = "purchase_orders"

    # PO Identification
    po_number: str = Field(unique=True, index=True)
    plex_po_id: Optional[str] = None

    # Vendor
    vendor_code: Optional[str] = None
    vendor_name: str = Field(index=True)

    # PO Type (for scenario handling)
    po_type: str = "standard"  # standard, blanket, service, freight

    # Dates
    po_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None

    # Amounts
    total_amount: float
    currency: str = "USD"

    # Status
    status: str = Field(default="open")  # open, partial, closed, cancelled

    # Line Items (JSON array)
    line_items: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))

    # Received quantities tracking
    received_items: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Raw Plex data
    plex_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Metadata
    department: Optional[str] = None
    project_code: Optional[str] = None
    notes: Optional[str] = None
```

#### **File 6: `backend/models/user.py`**
```python
"""
User Model - Authentication and authorization
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from .base import BaseModel

class User(BaseModel, table=True):
    """Application user"""
    __tablename__ = "users"

    # Identity
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    full_name: Optional[str] = None

    # Authentication
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False

    # Role-based access
    role: str = "user"  # user, manager, admin

    # Permissions
    can_approve: bool = False
    can_reject: bool = False
    can_edit: bool = True
    can_view_analytics: bool = True

    # Activity
    last_login: Optional[datetime] = None
    login_count: int = 0

    # Preferences
    email_notifications: bool = True
    auto_approve_threshold: float = 95.0
```

#### **File 7: `backend/models/audit_log.py`**
```python
"""
Audit Log Model - Complete audit trail for compliance
"""
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseModel

class AuditLog(BaseModel, table=True):
    """Audit trail for all actions"""
    __tablename__ = "audit_logs"

    # Who
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    user_email: Optional[str] = None

    # What
    action: str = Field(index=True)  # upload, parse, match, sync, approve, reject, edit
    entity_type: str  # vendor_invoice, plex_invoice, sync_operation
    entity_id: int

    # When
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Details
    before_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    after_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    changes: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    # Result
    success: bool = True
    error_message: Optional[str] = None

    # Metadata
    metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
```

#### **File 8: `backend/models/__init__.py`**
```python
"""
Models Package - Export all models
"""
from .base import BaseModel
from .vendor_invoice import VendorInvoice
from .plex_invoice import PlexInvoice
from .purchase_order import PurchaseOrder
from .sync_operation import SyncOperation
from .user import User
from .audit_log import AuditLog

__all__ = [
    "BaseModel",
    "VendorInvoice",
    "PlexInvoice",
    "PurchaseOrder",
    "SyncOperation",
    "User",
    "AuditLog",
]
```

---

### **PHASE 3: DATABASE SESSION**

#### **File 9: `backend/db/session.py`**
```python
"""
Database Session Management
Clean session handling with dependency injection
"""
from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
from config import settings

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
```

#### **File 10: `backend/db/__init__.py`**
```python
"""Database package"""
from .session import engine, create_db_and_tables, get_session

__all__ = ["engine", "create_db_and_tables", "get_session"]
```

---

### **PHASE 4: PLEX API CLIENT** ⭐ CRITICAL

#### **File 11: `backend/core/plex_client.py`**
```python
"""
Plex ERP API Client
Handles all interactions with Plex REST API
"""
import httpx
from typing import List, Dict, Any, Optional
from config import settings
from loguru import logger
import asyncio

class PlexClient:
    """
    Client for Plex ERP API

    Key Methods:
    - list_invoices_by_po() - Find all Plex invoices for a PO
    - get_received_invoices() - Get invoices with status "RECEIVED"
    - update_invoice_number() - Change invoice number from "RECEIVED" to actual
    - get_purchase_order() - Get PO details
    """

    def __init__(self):
        self.base_url = settings.plex_api_url
        self.api_key = settings.plex_api_key
        self.timeout = settings.plex_timeout
        self.retry_attempts = settings.plex_retry_attempts

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"

        for attempt in range(self.retry_attempts):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method,
                        url,
                        headers=self.headers,
                        **kwargs
                    )
                    response.raise_for_status()
                    return response.json()

            except httpx.HTTPError as e:
                logger.warning(f"Plex API error (attempt {attempt + 1}): {e}")
                if attempt == self.retry_attempts - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

        raise Exception("Max retry attempts reached")

    async def list_invoices_by_po(
        self,
        po_number: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all AP invoices for a specific PO

        Args:
            po_number: PO number to search
            status: Filter by status (e.g., "RECEIVED")

        Returns:
            List of invoice records from Plex
        """
        endpoint = settings.plex_invoice_endpoint
        params = {"po_number": po_number}

        if status:
            params["status"] = status

        result = await self._request("GET", endpoint, params=params)
        return result.get("invoices", [])

    async def get_received_invoices(
        self,
        po_number: str
    ) -> List[Dict[str, Any]]:
        """
        Get invoices with invoice_number = "RECEIVED" for a PO
        This is the target invoice we want to update
        """
        invoices = await self.list_invoices_by_po(po_number)

        # Filter for "RECEIVED" status invoices
        received = [
            inv for inv in invoices
            if inv.get("invoice_number") == "RECEIVED"
        ]

        logger.info(f"Found {len(received)} RECEIVED invoices for PO {po_number}")
        return received

    async def update_invoice_number(
        self,
        plex_invoice_id: str,
        new_invoice_number: str
    ) -> Dict[str, Any]:
        """
        Update Plex invoice number from "RECEIVED" to vendor invoice number

        Args:
            plex_invoice_id: Internal Plex invoice ID
            new_invoice_number: Vendor's actual invoice number

        Returns:
            Updated invoice data from Plex
        """
        endpoint = f"{settings.plex_invoice_endpoint}/{plex_invoice_id}"

        payload = {
            "invoice_number": new_invoice_number
        }

        logger.info(f"Updating Plex invoice {plex_invoice_id} to {new_invoice_number}")

        result = await self._request("PATCH", endpoint, json=payload)

        logger.success(f"Successfully updated invoice number")
        return result

    async def get_purchase_order(
        self,
        po_number: str
    ) -> Dict[str, Any]:
        """Get PO details from Plex"""
        endpoint = f"{settings.plex_po_endpoint}/{po_number}"
        return await self._request("GET", endpoint)

    async def sync_invoice(
        self,
        vendor_invoice_number: str,
        po_number: str
    ) -> Dict[str, Any]:
        """
        Main sync operation: Find RECEIVED invoice and update its number

        Args:
            vendor_invoice_number: Invoice number from vendor
            po_number: PO number

        Returns:
            {
                "success": bool,
                "updated_invoice": {...},
                "message": str
            }
        """
        try:
            # Step 1: Find RECEIVED invoices for this PO
            received_invoices = await self.get_received_invoices(po_number)

            if not received_invoices:
                return {
                    "success": False,
                    "message": f"No RECEIVED invoices found for PO {po_number}"
                }

            # Step 2: Update the first RECEIVED invoice
            # (In production, you may need more sophisticated matching logic)
            target_invoice = received_invoices[0]
            plex_invoice_id = target_invoice.get("id")

            # Step 3: Update invoice number in Plex
            updated_invoice = await self.update_invoice_number(
                plex_invoice_id,
                vendor_invoice_number
            )

            return {
                "success": True,
                "updated_invoice": updated_invoice,
                "message": f"Successfully updated invoice {plex_invoice_id}"
            }

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return {
                "success": False,
                "message": str(e),
                "error": str(e)
            }


# Singleton instance
plex_client = PlexClient()
```

---

### **PHASE 5: AI PARSER** ⭐ CRITICAL

#### **File 12: `backend/core/ai_parser.py`**
```python
"""
AI Invoice Parser using GPT-4 Vision
Extracts structured data from PDF/image invoices
"""
from openai import AsyncOpenAI
from typing import Dict, Any, List
from pathlib import Path
import base64
from config import settings
from loguru import logger

class AIParser:
    """
    GPT-4 Vision invoice parser

    Extracts:
    - Invoice number
    - Vendor name
    - Invoice date
    - Due date
    - Total amount
    - PO number(s)
    - Line items
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self.temperature = settings.openai_temperature

    async def parse_invoice(
        self,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Parse invoice from file

        Returns:
            {
                "invoice_number": str,
                "vendor_name": str,
                "invoice_date": str (YYYY-MM-DD),
                "due_date": str (YYYY-MM-DD),
                "total_amount": float,
                "po_numbers": [str],
                "line_items": [{...}],
                "confidence": float (0-100),
                "raw_text": str
            }
        """
        try:
            # Read file as base64
            with open(file_path, "rb") as f:
                file_data = base64.b64encode(f.read()).decode()

            # Determine file type
            file_type = Path(file_path).suffix.lower().replace(".", "")

            # Create prompt
            prompt = self._create_extraction_prompt()

            # Call GPT-4 Vision
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting structured data from invoices."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/{file_type};base64,{file_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            # Parse response
            result = self._parse_response(response)

            logger.success(f"Parsed invoice: {result.get('invoice_number')}")
            return result

        except Exception as e:
            logger.error(f"AI parsing failed: {e}")
            return {
                "error": str(e),
                "confidence": 0.0
            }

    def _create_extraction_prompt(self) -> str:
        """Create extraction prompt for GPT-4"""
        return """
Extract the following information from this invoice image:

1. Invoice Number
2. Vendor/Supplier Name
3. Invoice Date (format: YYYY-MM-DD)
4. Due Date (format: YYYY-MM-DD)
5. Total Amount (numeric value only)
6. Tax Amount (if shown)
7. Purchase Order Number(s) - look for "PO", "P.O.", "Order #", etc.
8. Line Items with: description, quantity, unit price, line total

Return the data as a JSON object with this exact structure:
{
    "invoice_number": "...",
    "vendor_name": "...",
    "invoice_date": "YYYY-MM-DD",
    "due_date": "YYYY-MM-DD",
    "total_amount": 0.00,
    "tax_amount": 0.00,
    "subtotal": 0.00,
    "po_numbers": ["PO-123", "PO-456"],
    "line_items": [
        {
            "line_number": 1,
            "description": "...",
            "quantity": 0.00,
            "unit_price": 0.00,
            "line_total": 0.00
        }
    ],
    "raw_text": "all visible text on invoice",
    "confidence": 0-100 (your confidence in the extraction)
}

Important:
- If a field is not found, use null
- For po_numbers, search entire invoice including footer notes
- For line_items, extract ALL items shown
- Confidence should reflect clarity of the image and data
"""

    def _parse_response(self, response) -> Dict[str, Any]:
        """Parse GPT-4 response into structured data"""
        content = response.choices[0].message.content

        # Try to extract JSON from response
        import json
        import re

        # Find JSON in response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data

        # Fallback: return raw content
        return {
            "raw_text": content,
            "confidence": 50.0,
            "error": "Could not parse structured data"
        }


# Singleton instance
ai_parser = AIParser()
```

---

## 🧪 TESTS

### **File 13: `backend/tests/conftest.py`**
```python
"""
Pytest configuration and fixtures
"""
import pytest
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient

@pytest.fixture(name="session")
def session_fixture():
    """Create test database session"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with database session"""
    from main import app
    from db.session import get_session

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
```

### **File 14: `backend/tests/test_plex_client.py`**
```python
"""
Tests for Plex API Client
"""
import pytest
from core.plex_client import PlexClient

@pytest.mark.asyncio
async def test_get_received_invoices():
    """Test finding RECEIVED invoices"""
    client = PlexClient()

    # Mock or use test PO number
    invoices = await client.get_received_invoices("PO-TEST-001")

    assert isinstance(invoices, list)

@pytest.mark.asyncio
async def test_update_invoice_number():
    """Test updating invoice number"""
    client = PlexClient()

    result = await client.update_invoice_number(
        plex_invoice_id="test-123",
        new_invoice_number="INV-2024-001"
    )

    assert result["success"] == True

@pytest.mark.asyncio
async def test_sync_invoice():
    """Test full sync workflow"""
    client = PlexClient()

    result = await client.sync_invoice(
        vendor_invoice_number="INV-2024-001",
        po_number="PO-TEST-001"
    )

    assert "success" in result
```

### **File 15: `backend/tests/test_api_sync.py`**
```python
"""
Tests for Sync API
"""
def test_sync_invoice(client):
    """Test POST /api/sync"""
    response = client.post(
        "/api/sync",
        json={
            "vendor_invoice_id": 1,
            "po_number": "PO-TEST-001"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
```

---

## 🚀 GETTING STARTED IN CURSOR

### **Step 1: Open Project**
```bash
cd C:\Users\cahil\PlexSync-AI
cursor .
```

### **Step 2: Install Dependencies**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### **Step 3: Setup Environment**
```bash
cp .env.example .env
# Edit .env with your values
```

### **Step 4: Start Building**
Use Cursor AI to help build each file following this guide.

Start with: **Phase 2 - Database Models**

---

## 💡 CURSOR TIPS

### **Use Composer Mode**
1. Open Cursor Composer (Cmd/Ctrl + I)
2. Reference this guide: `@CURSOR_BUILD_GUIDE.md`
3. Ask: "Create backend/models/vendor_invoice.py following the spec"

### **Multi-File Edits**
1. Select multiple files in sidebar
2. Right-click → "Edit with Cursor"
3. Make coordinated changes across files

### **Run Tests As You Go**
```bash
pytest backend/tests/test_models.py -v
```

---

## ✅ VALIDATION CHECKLIST

Before moving to next phase:
- [ ] All models created and tested
- [ ] Database migrations working
- [ ] Plex client can connect
- [ ] AI parser extracts data
- [ ] API endpoints respond
- [ ] Tests pass (>80% coverage)
- [ ] Frontend builds
- [ ] Can upload invoice end-to-end
- [ ] Can sync to Plex end-to-end

---

**Ready to build in Cursor!** 🚀
