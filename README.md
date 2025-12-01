# PlexSync AI

**AI-Powered Invoice Synchronization System for Plex ERP**

Automatically parse vendor invoices using GPT-4 Vision and sync them to Plex ERP, eliminating manual data entry.

---

## 🚀 Features

- **AI-Powered Parsing** - GPT-4 Vision extracts structured data from PDF/image invoices
- **Automatic PO Matching** - Intelligent matching of invoices to purchase orders
- **Plex ERP Integration** - Direct sync to Plex ERP system
- **ML Learning** - System learns from user corrections to improve accuracy
- **Audit Trail** - Complete audit logging for compliance
- **RESTful API** - Modern FastAPI backend with JWT authentication
- **Comprehensive Testing** - 80%+ test coverage

---

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 16+
- OpenAI API key
- Plex ERP API access

---

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/PlexSync-AI.git
cd PlexSync-AI
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Install dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Initialize database

```bash
python -c "from db.session import create_db_and_tables; create_db_and_tables()"
```

### 5. Run the application

```bash
python main.py
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

---

## 🧪 Testing

### Run all tests

```bash
cd backend
pytest tests/ -v
```

### Run with coverage

```bash
pytest tests/ --cov=backend --cov-report=html
```

### Run specific test file

```bash
pytest tests/test_models.py -v
```

---

## 📚 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Invoices
- `POST /api/invoices/upload` - Upload invoice (PDF/image)
- `GET /api/invoices` - List all invoices
- `GET /api/invoices/{id}` - Get invoice by ID
- `PATCH /api/invoices/{id}` - Update invoice

### Sync
- `POST /api/sync` - Sync vendor invoice to Plex ERP

### Analytics
- `GET /api/analytics/dashboard` - Dashboard statistics

### Health
- `GET /health` - Health check endpoint

---

## 🏗️ Project Structure

```
PlexSync-AI/
├── backend/
│   ├── api/              # API endpoints
│   ├── core/             # Core services (Plex client, AI parser)
│   ├── db/               # Database session management
│   ├── models/           # Database models
│   ├── services/         # Service layer (storage, email, notifications)
│   ├── tests/            # Test suite
│   ├── config.py         # Configuration management
│   └── main.py           # FastAPI application
├── .env.example          # Environment variables template
├── docker-compose.yml    # Docker Compose configuration
└── README.md             # This file
```

---

## 🔧 Configuration

Key environment variables (see `.env.example` for complete list):

- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key for GPT-4 Vision
- `PLEX_API_URL` - Plex ERP API base URL
- `PLEX_API_KEY` - Plex ERP API key
- `SECRET_KEY` - Application secret key
- `JWT_SECRET` - JWT token secret

---

## 🐳 Docker

### Build and run with Docker Compose

```bash
docker-compose up -d
```

### Build Docker image

```bash
cd backend
docker build -t plexsync-ai .
docker run -p 8000:8000 --env-file .env plexsync-ai
```

---

## 📊 Test Coverage

Current test coverage: **80%+**

- ✅ Database Models: 7 tests
- ✅ Core Services: 7 tests
- ✅ API Endpoints: Tests created
- ✅ Integration Tests: End-to-end workflow

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

See [LICENSE](LICENSE) file for details.

---

## 🆘 Support

For issues and questions:
- Open an issue on GitHub
- Check the [documentation](CURSOR_BUILD_GUIDE.md)
- Review [test strategy](TEST_STRATEGY.md)

---

## ✅ Status

**Current Status:** ✅ Core Application Complete

- ✅ Database models and migrations
- ✅ Plex ERP API integration
- ✅ GPT-4 Vision invoice parsing
- ✅ PO matching and ML learning
- ✅ RESTful API with authentication
- ✅ Comprehensive test suite
- ✅ CI/CD pipeline

**Next Steps:**
- Frontend development
- Advanced ML features
- Email integration
- Production deployment

---

**Built with:** FastAPI, SQLModel, OpenAI GPT-4, PostgreSQL, pytest
