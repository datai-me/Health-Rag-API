# 🩺 Health RAG API

A professional, production-ready RAG (Retrieval-Augmented Generation) API for medical information using FastAPI, LangChain, and OpenFDA.

## 🌟 Features

- **🔐 Secure Authentication**: JWT-based authentication with bcrypt password hashing
- **🤖 RAG Architecture**: Advanced retrieval-augmented generation for accurate answers
- **💊 FDA Integration**: Automatic data fetching from OpenFDA API
- **📊 Vector Database**: ChromaDB for efficient similarity search
- **🚀 Production-Ready**: Comprehensive error handling, logging, and validation
- **📝 Clean Architecture**: Layered architecture with separation of concerns
- **🔧 Configurable**: Environment-based configuration management
- **📚 Well-Documented**: OpenAPI/Swagger documentation included

## 🏗️ Architecture

```
app/
├── core/              # Core functionality (config, security, exceptions)
├── api/               # API layer (endpoints, dependencies)
├── schemas/           # Pydantic models (DTOs)
├── models/            # SQLAlchemy models
├── services/          # Business logic
├── repositories/      # Data access layer
└── db/                # Database configuration
```

### Design Patterns Used

- **Repository Pattern**: Abstracts data access logic
- **Dependency Injection**: Clean dependency management with FastAPI
- **Service Layer**: Business logic separated from API layer
- **DTO Pattern**: Request/Response validation with Pydantic schemas

## 🛠️ Technology Stack

- **Backend**: FastAPI
- **Database**: SQLAlchemy (SQLite by default, PostgreSQL recommended for production)
- **Authentication**: JWT + bcrypt
- **LLM**: Groq (Llama 3.3 70B)
- **Embeddings**: Jina AI embeddings
- **Vector Store**: ChromaDB
- **Orchestration**: LangChain
- **Package Management**: Poetry

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Poetry
- Groq API key ([Get one here](https://console.groq.com))
- Jina API key ([Get one here](https://jina.ai))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd health_rag_api
   ```

2. **Install dependencies with Poetry**
   ```bash
   poetry install
   ```

3. **Activate the virtual environment**
   ```bash
   poetry shell
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

5. **Generate a secure SECRET_KEY**
   ```bash
   openssl rand -hex 32
   # Copy the output to SECRET_KEY in .env
   ```

6. **Run the application**
   ```bash
   # Development mode with auto-reload
   uvicorn app.main:app --reload

   # Production mode
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

7. **Access the API**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## 📖 API Usage

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecureP@ss123"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=SecureP@ss123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Ingest Drug Data

```bash
curl -X POST "http://localhost:8000/api/v1/rag/ingest" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "drug_name": "aspirin"
  }'
```

### 4. Ask Questions

```bash
curl -X POST "http://localhost:8000/api/v1/rag/ask" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the side effects of aspirin?"
  }'
```

## 🔧 Configuration

All configuration is managed through environment variables. See `.env.example` for available options.

### Key Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT secret key (required) | - |
| `GROQ_API_KEY` | Groq API key | - |
| `JINA_API_KEY` | Jina embeddings API key | - |
| `DATABASE_URL` | Database connection URL | `sqlite:///./health_rag.db` |
| `ENVIRONMENT` | Environment (development/production) | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |

## 🧪 Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_auth.py
```

## 📝 Code Quality

### Format Code

```bash
# Format with Black
poetry run black app/

# Sort imports with isort
poetry run isort app/

# Lint with flake8
poetry run flake8 app/

# Type check with mypy
poetry run mypy app/
```

## 🚀 Production Deployment

### Recommended Changes for Production

1. **Use PostgreSQL instead of SQLite**
   ```
   DATABASE_URL=postgresql://user:password@localhost/dbname
   ```

2. **Set strong SECRET_KEY**
   ```bash
   openssl rand -hex 32
   ```

3. **Configure CORS properly**
   ```
   ALLOWED_ORIGINS=https://yourdomain.com
   ```

4. **Set environment to production**
   ```
   ENVIRONMENT=production
   DEBUG=false
   ```

5. **Use a process manager**
   ```bash
   # Using Gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

## 🔒 Security Features

- ✅ Password hashing with bcrypt
- ✅ JWT token authentication
- ✅ Password strength validation
- ✅ Input validation with Pydantic
- ✅ SQL injection protection via SQLAlchemy ORM
- ✅ CORS configuration
- ✅ Rate limiting ready (add middleware)

## 📊 Logging

The application uses structured logging with configurable levels:

```python
# Logs are output to stdout in JSON format (configurable)
# Available levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenFDA for providing public drug information
- Groq for fast LLM inference
- Jina AI for embeddings
- FastAPI team for the amazing framework
- LangChain for RAG orchestration

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

## 🗺️ Roadmap

- [ ] Add user roles and permissions
- [ ] Implement rate limiting
- [ ] Add caching layer (Redis)
- [ ] Database migrations with Alembic
- [ ] Async database operations
- [ ] WebSocket support for streaming responses
- [ ] Docker containerization
- [ ] Kubernetes deployment configs
- [ ] Comprehensive integration tests
- [ ] Performance monitoring
