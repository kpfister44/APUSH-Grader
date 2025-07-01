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

- Python 3.11 or higher
- pip

### Installation

1. **Create virtual environment**:
   ```bash
   cd backend
   python -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
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
# Start development server with auto-reload
uvicorn app.main:app --reload

# Or run with Python
python -m app.main

# Application will be available at:
# - API: http://localhost:8000
# - Interactive docs: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

### Running tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_health.py
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

- ✅ FastAPI application setup
- ✅ Health check endpoint
- ✅ Configuration management
- ✅ Basic testing framework
- ✅ Project structure
- 📋 Essay processing logic (Phase 1B)
- 📋 AI service integration (Phase 2)
- 📋 Grading endpoints (Phase 2)