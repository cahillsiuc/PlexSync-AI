# PlexSync AI - Deployment Guide

Production deployment guide for PlexSync AI.

---

## 🚀 Deployment Options

### Option 1: Docker (Recommended)

#### Build Image
```bash
cd backend
docker build -t plexsync-ai:latest .
```

#### Run Container
```bash
docker run -d \
  --name plexsync-ai \
  -p 8000:8000 \
  --env-file .env.production \
  --restart unless-stopped \
  plexsync-ai:latest
```

#### Docker Compose (Production)
```yaml
version: '3.8'

services:
  app:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - .env.production
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: plexsync
      POSTGRES_USER: plexsync
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

volumes:
  postgres_data:
```

---

### Option 2: Cloud Platforms

#### Heroku

1. **Create Procfile**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. **Deploy**
```bash
heroku create plexsync-ai
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set OPENAI_API_KEY=your-key
heroku config:set PLEX_API_KEY=your-key
git push heroku main
```

#### AWS (ECS/Fargate)

1. **Build and Push to ECR**
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker build -t plexsync-ai .
docker tag plexsync-ai:latest <account>.dkr.ecr.us-east-1.amazonaws.com/plexsync-ai:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/plexsync-ai:latest
```

2. **Create ECS Task Definition** with environment variables

#### Google Cloud Run

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/plexsync-ai
gcloud run deploy plexsync-ai \
  --image gcr.io/PROJECT_ID/plexsync-ai \
  --platform managed \
  --region us-central1 \
  --set-env-vars DATABASE_URL=...,OPENAI_API_KEY=...
```

---

## 🔒 Production Checklist

### Security
- [ ] Change all default secrets (`SECRET_KEY`, `JWT_SECRET`)
- [ ] Use strong database passwords
- [ ] Enable HTTPS/TLS
- [ ] Set up firewall rules
- [ ] Configure CORS properly (restrict origins)
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerting
- [ ] Regular security updates

### Database
- [ ] Use managed PostgreSQL (RDS, Cloud SQL, etc.)
- [ ] Enable automated backups
- [ ] Set up connection pooling
- [ ] Configure read replicas (if needed)
- [ ] Set up database migrations (Alembic)

### Environment Variables
- [ ] Store secrets in secure vault (AWS Secrets Manager, etc.)
- [ ] Never commit `.env` files
- [ ] Use different environments (dev, staging, prod)
- [ ] Rotate API keys regularly

### Monitoring
- [ ] Set up application monitoring (Sentry, DataDog, etc.)
- [ ] Configure log aggregation
- [ ] Set up health check endpoints
- [ ] Monitor API response times
- [ ] Track error rates

### Performance
- [ ] Enable Redis caching
- [ ] Configure CDN for static files
- [ ] Set up load balancing (if needed)
- [ ] Optimize database queries
- [ ] Enable connection pooling

---

## 📊 Health Checks

### Application Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production"
}
```

### Database Health
```bash
# Check database connection
python -c "from db.session import engine; engine.connect()"
```

---

## 🔄 Database Migrations

### Using Alembic

1. **Initialize Alembic** (if not already)
```bash
cd backend
alembic init alembic
```

2. **Create Migration**
```bash
alembic revision --autogenerate -m "Initial migration"
```

3. **Apply Migrations**
```bash
alembic upgrade head
```

---

## 📈 Scaling

### Horizontal Scaling
- Use load balancer (nginx, AWS ALB, etc.)
- Run multiple app instances
- Use shared Redis for sessions
- Use managed database with read replicas

### Vertical Scaling
- Increase container/instance size
- Optimize database queries
- Add caching layer
- Use connection pooling

---

## 🔐 SSL/TLS Setup

### Using Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl http2;
    server_name plexsync.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🚨 Backup Strategy

### Database Backups
```bash
# Automated daily backup
pg_dump -h localhost -U postgres plexsync > backup_$(date +%Y%m%d).sql

# Restore
psql -h localhost -U postgres plexsync < backup_20240101.sql
```

### File Storage Backups
- Use cloud storage (S3, GCS, etc.)
- Enable versioning
- Set up lifecycle policies
- Regular backup verification

---

## 📝 Environment-Specific Configs

### Development
```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

### Staging
```env
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
```

### Production
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
SENTRY_ENABLED=true
```

---

## 🎯 Post-Deployment

1. **Verify Health**
   ```bash
   curl https://your-domain.com/health
   ```

2. **Test API**
   ```bash
   curl https://your-domain.com/api/invoices
   ```

3. **Monitor Logs**
   ```bash
   docker logs -f plexsync-ai
   # or
   tail -f logs/plexsync.log
   ```

4. **Set Up Alerts**
   - Application errors
   - High response times
   - Database connection issues
   - Disk space warnings

---

## 🔄 Updates and Rollbacks

### Rolling Update
```bash
# Build new version
docker build -t plexsync-ai:v2.0.0 .

# Deploy with zero downtime
docker-compose up -d --no-deps app
```

### Rollback
```bash
# Revert to previous version
docker-compose up -d --no-deps app --scale app=1
```

---

**Ready for production!** 🚀

