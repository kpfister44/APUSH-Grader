# APUSH Grader Backend

Python FastAPI backend for the APUSH Grader application. This backend provides AI-powered grading for AP US History essays.

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config/
│   │   └── settings.py         # Pydantic settings management
│   ├── models/
│   │   ├── core/               # Core data models
│   │   │   ├── essay_types.py  # Essay type enum & rules
│   │   │   └── grade_models.py # Grade response models
│   │   └── requests/
│   │       └── health.py       # Health check models
│   └── api/
│       ├── deps.py             # Dependency injection
│       └── routes/
│           └── health.py       # Health check endpoint
├── tests/                      # Test suite
├── requirements.txt            # Core dependencies
├── requirements-dev.txt        # Development dependencies
├── .env.example                # Environment template
└── README.md                   # This file
```

## Setup

### Prerequisites

- Python 3.12 (recommended for M-series Mac compatibility)
- pip

### Installation

1. **Create virtual environment**:
   ```bash
   cd backend
   python3.12 -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

## Development

### Running the application

```bash
# Ensure you're in the backend directory and virtual environment is activated
cd backend
source venv/bin/activate

# Start development server with auto-reload
uvicorn app.main:app --reload

# Or specify port if 8000 is in use
uvicorn app.main:app --reload --port 8001

# Application will be available at:
# - API: http://localhost:8000
# - Interactive docs: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
# - Health check: http://localhost:8000/health
```

### Running tests

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Run all tests with verbose output
pytest tests/ -v

# Run integration tests only
pytest tests/integration/ -v

# Run tests with short traceback
pytest tests/ --tb=short

# Run specific test file
pytest tests/test_health.py -v
```

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Type checking
mypy app/

# Run all quality checks
black . && isort . && mypy app/ && pytest
```

## API Endpoints

### Health Check

- **GET** `/health` - Returns application health status
- **GET** `/` - Root endpoint with basic info

Example health response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "services": {
    "openai": "configured",
    "anthropic": "configured"
  }
}
```

## Configuration

Environment variables (see `.env.example`):

- `ENVIRONMENT` - Environment name (development/production)
- `DEBUG` - Enable debug mode
- `LOG_LEVEL` - Logging level
- `API_HOST` - API host (default: 0.0.0.0)
- `API_PORT` - API port (default: 8000)
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `ALLOWED_ORIGINS` - CORS allowed origins

## Next Steps

This is Phase 1A of the migration plan. Next phases will add:

- **Phase 1B**: Swift model migration to Python
- **Phase 1C**: Essay processing business logic
- **Phase 2**: AI service integration
- **Phase 3**: iOS app integration
- **Phase 4**: Deployment

## Development Status

**Phase 3 COMPLETE** - Production Ready Backend

- ✅ FastAPI application setup with middleware
- ✅ Complete grading workflow (POST /api/v1/grade)
- ✅ Health check endpoints (/health, /health/detailed, /usage/summary)
- ✅ Real Anthropic Claude 3.5 Sonnet integration
- ✅ Production features: rate limiting, structured logging, usage safeguards
- ✅ Comprehensive test suite (320+ tests)
- ✅ Essay processing for DBQ, LEQ, SAQ types
- ✅ Multi-part SAQ support
- ✅ iOS frontend integration complete
- ✅ Configuration management with environment variables
- ✅ Error handling and user-friendly messages