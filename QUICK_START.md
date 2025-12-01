# PlexSync AI - Quick Start Guide

Get up and running in 5 minutes! 🚀

---

## ⚡ Quick Setup

### 1. Clone and Navigate
```bash
git clone https://github.com/yourusername/PlexSync-AI.git
cd PlexSync-AI
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values (minimum required):
# - DATABASE_URL
# - SECRET_KEY
# - JWT_SECRET
# - OPENAI_API_KEY
# - PLEX_API_URL
# - PLEX_API_KEY
```

### 3. Install Dependencies
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Initialize Database
```bash
python -c "from db.session import create_db_and_tables; create_db_and_tables()"
```

### 5. Run the Server
```bash
python main.py
```

**🎉 Server running at:** `http://localhost:8000`

**📚 API Docs:** `http://localhost:8000/docs`

---

## 🧪 Quick Test

### Run Tests
```bash
pytest tests/ -v
```

### Expected Output
```
14 passed in 2.84s
```

---

## 🔑 First Steps

### 1. Register a User
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "admin",
    "password": "SecurePass123!"
  }'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=SecurePass123!"
```

Save the `access_token` from the response.

### 3. Upload an Invoice
```bash
curl -X POST "http://localhost:8000/api/invoices/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/invoice.pdf"
```

### 4. Sync to Plex
```bash
curl -X POST "http://localhost:8000/api/sync" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vendor_invoice_id": 1,
    "po_number": "PO-2024-100"
  }'
```

---

## 🐳 Docker Quick Start

### Using Docker Compose
```bash
docker-compose up -d
```

### Using Docker
```bash
cd backend
docker build -t plexsync-ai .
docker run -p 8000:8000 --env-file .env plexsync-ai
```

---

## 📋 Environment Variables Checklist

Minimum required for basic functionality:

- [ ] `DATABASE_URL` - PostgreSQL connection string
- [ ] `SECRET_KEY` - Random secret key (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- [ ] `JWT_SECRET` - JWT signing secret (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- [ ] `OPENAI_API_KEY` - Your OpenAI API key
- [ ] `PLEX_API_URL` - Plex ERP API base URL
- [ ] `PLEX_API_KEY` - Plex ERP API key

Optional (have defaults):
- `STORAGE_PATH` - File storage location (default: `./storage/invoices`)
- `LOG_LEVEL` - Logging level (default: `INFO`)
- `API_PORT` - Server port (default: `8000`)

---

## 🔧 Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT 1"

# Verify DATABASE_URL in .env
echo $DATABASE_URL
```

### Import Errors
```bash
# Make sure you're in the backend directory
cd backend

# Verify virtual environment is activated
which python  # Should show venv path
```

### Test Failures
```bash
# Run with verbose output
pytest tests/ -v --tb=short

# Run specific test file
pytest tests/test_models.py -v
```

### Port Already in Use
```bash
# Change port in .env
API_PORT=8001

# Or kill process using port 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill
```

---

## 📚 Next Steps

1. **Explore API Docs** - Visit `http://localhost:8000/docs` for interactive API documentation
2. **Review Test Suite** - Check `backend/tests/` for examples
3. **Read Documentation** - See `CURSOR_BUILD_GUIDE.md` and `BUILD_SUMMARY.md`
4. **Set Up CI/CD** - Push to GitHub to trigger automated tests

---

## 🆘 Need Help?

- **Documentation:** See `README.md` and `BUILD_SUMMARY.md`
- **Test Strategy:** See `TEST_STRATEGY.md`
- **Build Guide:** See `CURSOR_BUILD_GUIDE.md`
- **Issues:** Open an issue on GitHub

---

**Happy coding!** 🎉

