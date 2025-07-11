# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
APUSH Grader - Migrating from iOS SwiftUI app to **Python FastAPI backend + iOS frontend** architecture. Uses AI (OpenAI/Anthropic) to grade AP US History essays based on College Board rubrics.

## Target Audience and Scope
APUSH Grader is designed for a small handful of teacher to use it. Anywhere from 2-12 teachers. Prioritize simplicity over complexity whenever possible. Functionality is more important than comprehensiveness and minimize complexity wherever possible. This is NOT meant to be a full scale enterprise project that can support 1000's of users!

## Current Architecture Status
**Phase 1 COMPLETE**: Python backend with comprehensive API and testing
**Phase 2A COMPLETE**: Real Anthropic AI service integration implemented
**Phase 2B COMPLETE**: Production configuration, rate limiting, logging, and monitoring implemented
**Phase 2C COMPLETE**: Real API testing, documentation, and deployment guides
**Phase 3 COMPLETE**: iOS frontend migration to Python backend API - APUSHGraderCore replaced
**Phase 4 READY**: Production deployment and monitoring

## Repository Structure

### **backend/** - Python FastAPI Backend (PRODUCTION READY)
- **app/main.py** - FastAPI application entry point with middleware
- **app/api/routes/** - API endpoints
  - **grading.py** - POST /api/v1/grade endpoint (complete workflow with rate limiting)
  - **health.py** - Health check endpoints (/health, /health/detailed, /usage/summary)
- **app/middleware/** - Production middleware
  - **rate_limiting.py** - SlowAPI rate limiting (20 req/min, 50 essays/hour)
  - **logging.py** - Request logging with correlation IDs
  - **usage_limiting.py** - Daily usage limits (100 essays/day, 50k words/day)
- **app/models/** - Pydantic data models
  - **core/** - Core business models (essay_types, grade_models, api_models)
  - **processing/** - Processing models (response, display, preprocessing)
  - **requests/** - API request/response models (grading, health)
- **app/services/** - Business logic services
  - **api/coordinator.py** - End-to-end workflow orchestration
  - **processing/essay/** - Essay processing (validator, analyzer, cleaner, warnings)
  - **processing/prompt/generator.py** - Essay-specific AI prompt generation
  - **processing/response/** - AI response processing (validator, insights, formatter)
  - **logging/structured_logger.py** - JSON logging with correlation IDs and performance tracking
  - **usage/tracker.py** - Usage tracking and daily limits enforcement
  - **dependencies/service_locator.py** - Dependency injection container
- **tests/** - Comprehensive test suite (320+ tests)
  - **integration/** - End-to-end workflow tests + production feature tests
  - **services/processing/prompt/** - Prompt generation tests
  - All other test suites for models and services
- **requirements.txt** - Core dependencies (FastAPI, Pydantic, uvicorn, anthropic, slowapi)
- **requirements-dev.txt** - Development tools (pytest, black, mypy)

### **APUSHGrader/** - iOS App (UI Layer - API Integration Complete)
- **Models/** - Simple API DTOs matching Python backend
- **Services/NetworkService.swift** - HTTP client for Python backend API
- **Views/** - SwiftUI interface using API responses
- **Current**: Uses Python backend via HTTP API (localhost:8000)

## Python Backend Commands

### **Development Environment Setup**
```bash
cd backend
# Create virtual environment (use Python 3.12 for compatibility)
python3.12 -m venv venv               # Create virtual environment
source venv/bin/activate              # Activate Python virtual environment
pip install --upgrade pip            # Upgrade pip to latest version
pip install -r requirements.txt       # Install core dependencies  
pip install -r requirements-dev.txt   # Install development tools
```

**Important**: Always ensure you're in the `/backend/` directory and the virtual environment is activated before running any Python commands.

**Note**: Use Python 3.12 instead of 3.13 for better package compatibility on M-series Macs.

### **Running the Server**
```bash
# Method 1: From project root
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Method 2: If already in backend directory
source venv/bin/activate
uvicorn app.main:app --reload

# Use different port if 8000 is in use
uvicorn app.main:app --reload --port 8001

# Server will be available at:
# - API: http://localhost:8000
# - Interactive docs: http://localhost:8000/docs  
# - Health check: http://localhost:8000/health
```

**Note**: The server must be running for the iOS app to connect. If you see connection errors in the iOS app, verify the backend is running and accessible.

### **Testing**
```bash
# Ensure you're in backend directory with virtual environment activated
cd backend
source venv/bin/activate

pytest tests/ -v                      # Run all tests with verbose output
pytest tests/integration/ -v          # Run integration tests only
pytest tests/services/processing/prompt/ -v  # Run prompt generation tests only
pytest tests/ --tb=short              # Run with short traceback format
```

**Important**: Always activate the virtual environment before running tests to ensure all dependencies are available.

### **API Testing**
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health
- **Detailed Health**: http://localhost:8000/health/detailed
- **Usage Summary**: http://localhost:8000/usage/summary
- **Grade Endpoint**: POST http://localhost:8000/api/v1/grade (rate limited)

## iOS App Commands
- **iOS App**: ⌘+B in Xcode to build, ⌘+R to run
- **Testing**: Use SwiftUI previews for quick API testing (calls real backend)
- **Backend Required**: Ensure Python backend is running on localhost:8000

## Git and GitHub Workflow

### **Creating Feature Branches**
```bash
git checkout -b feature/your-feature-name
# Make your changes
git add path/to/changed/files
git commit -m "Your commit message"
```

### **Pushing and Creating Pull Requests**
```bash
# If authentication issues occur, authenticate with GitHub CLI first:
echo "your-github-token" | gh auth login --with-token

# Set remote URL with token for authentication (if needed)
git remote set-url origin https://your-github-token@github.com/kpfister44/APUSH-Grader.git

# Push feature branch
git push -u origin feature/your-feature-name

# Create pull request using GitHub CLI
gh pr create --title "Your PR Title" --body "Your PR description" --head feature/your-feature-name --base main

# Merge PR (squash and delete branch)
gh pr merge PR_NUMBER --squash --delete-branch

# Switch back to main and pull latest
git checkout main
git pull origin main
```

### **GitHub CLI Authentication**
If you encounter authentication issues with git push, use GitHub CLI:
```bash
# Authenticate with your personal access token
echo "ghp_your_token_here" | gh auth login --with-token

# Verify authentication
gh auth status

# Set repository default
gh repo set-default kpfister44/APUSH-Grader
```

### **Alternative: Manual Git with Token**
If GitHub CLI isn't available, you can authenticate git directly:
```bash
git remote set-url origin https://ghp_your_token_here@github.com/kpfister44/APUSH-Grader.git
git push -u origin your-branch-name
```

**Note**: Replace `ghp_your_token_here` with your actual GitHub Personal Access Token.

## Testing Status

### **Python Backend Testing (PRODUCTION READY)**
✅ **320+ Comprehensive Tests** - All passing with full coverage
- **19 PromptGenerator Tests** - Essay-specific prompt generation and validation
- **49 Integration Tests** - End-to-end API workflow + production features testing  
- **69 Response Processing Tests** - AI response processing services
- **94 Core Processing Tests** - Essay validation, text analysis, warning generation
- **88+ Model Tests** - Data model validation and business logic
- **Production Feature Tests** - Rate limiting, structured logging, usage safeguards, health monitoring

### **iOS App Testing**
✅ **SwiftUI Integration** - iOS app successfully connects to Python backend
- NetworkService handles HTTP API communication
- Real-time testing possible via SwiftUI previews
- All business logic now handled by Python backend API

## Essay Types Supported
- **DBQ** (Document-Based Question) - 6 points
- **LEQ** (Long Essay Question) - 6 points  
- **SAQ** (Short Answer Question) - 3 points

## Current Status - Phase 3 COMPLETE ✅

### **✅ Python Backend (PRODUCTION READY)**
- **Complete FastAPI Backend** - Full grading workflow with 320+ passing tests
- **Production Features** - Rate limiting, structured logging, usage safeguards, health monitoring
- **API Endpoints** - POST /api/v1/grade (rate limited), health endpoints, usage monitoring
- **Real AI Integration** - Anthropic Claude 3.5 Sonnet with comprehensive testing
- **Service Architecture** - Clean dependency injection with protocol-based interfaces
- **Comprehensive Testing** - End-to-end integration tests + real API validation
- **Production Documentation** - Deployment guides, cost documentation, API usage guides

### **✅ Migration Milestones Completed**
- **Phase 1A Complete** - Python FastAPI project structure and foundation
- **Phase 1B Complete** - Swift models migration to Python (88 tests)
- **Phase 1C-1 Complete** - Core processing services (essay validation, text analysis)
- **Phase 1C-2 Complete** - Response processing services (validation, insights, formatting)
- **Phase 1C-3 Complete** - Prompt generation & complete API integration (34 tests)
- **Phase 2A Complete** - Real Anthropic AI service integration implemented
- **Phase 2B Complete** - Production readiness (rate limiting, logging, usage safeguards, monitoring)
- **Phase 2C Complete** - Real API testing, documentation, and deployment guides
- **Phase 3 Complete** - iOS frontend migration to Python backend API, APUSHGraderCore removed

### **🔧 Development Environment**
- **AI Service Configuration**: Switch between mock and real AI (see AI Configuration section below)
- **API Keys**: Anthropic API key required for real AI integration
- **Server**: `uvicorn app.main:app --reload` for development
- **Testing**: `pytest tests/ -v` for comprehensive test suite

## Migration Progress

**Current Status**: Phase 3 COMPLETE ✅ - iOS frontend successfully migrated to Python backend API

### **Target Architecture (ACHIEVED)**
```
iOS Frontend (SwiftUI) → HTTP API → Python Backend (FastAPI) → Mock AI / Real Anthropic AI (configurable)
                                      ↓
                              Production Features:
                              • Rate Limiting (20 req/min, 50 essays/hour)
                              • Structured Logging (JSON + correlation IDs)
                              • Usage Safeguards (100 essays/day, 50k words/day)
                              • Health Monitoring (/health, /health/detailed)
```

### **Next Steps**
- **Phase 4**: Production deployment and monitoring
- **Future**: Web frontend expansion, additional features

**See PLAN.md for detailed migration timeline and implementation details.**

## Architecture Benefits
- **Clean Service Architecture**: Protocol-based dependency injection with service locator pattern
- **Comprehensive Testing**: 320+ tests covering all components with mock AI integration and production features
- **Platform-Agnostic Design**: Backend ready for multiple frontends (iOS, web, etc.)
- **Production Ready**: Complete API with rate limiting, structured logging, usage safeguards, and health monitoring
- **Cost Protection**: Daily limits and usage tracking to prevent excessive Anthropic API costs
- **Operational Visibility**: Structured logging, correlation IDs, and health endpoints for monitoring
- **Teacher-Friendly**: Generous limits (100 essays/day) with user-friendly error messages
- **Maintainable Codebase**: Python ecosystem easier than complex Swift/iOS
- **Scalable Design**: Easy to add new features without affecting existing components

## AI Configuration

### **Switching Between Mock and Real AI**

The system supports two AI service modes that can be configured via environment variables:

#### **Mock AI (Default - No API Key Required)**
```bash
# Default mode - uses realistic mock responses for testing
AI_SERVICE_TYPE=mock
```

#### **Real Anthropic AI (Requires API Key)**
```bash
# Real AI mode - uses Claude 3.5 Sonnet for actual grading
AI_SERVICE_TYPE=anthropic
ANTHROPIC_API_KEY=your-actual-api-key-here
```

### **Environment Configuration**
Create a `.env` file in the `/backend/` directory:
```bash
# For development with mock AI (default)
AI_SERVICE_TYPE=mock

# For production with real AI
AI_SERVICE_TYPE=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

### **AI Service Features**
- **Mock AI**: Provides consistent, realistic responses for all essay types (DBQ/LEQ/SAQ)
- **Anthropic AI**: Uses Claude 3.5 Sonnet model (anthropic==0.57.1) with temperature=0.3, max_tokens=1500
- **Seamless Switching**: Same API interface works with both mock and real AI
- **Error Handling**: Graceful fallback and user-friendly error messages
- **Testing**: All existing tests work with both AI service types

### **API Usage & Costs**

#### **Anthropic Claude 3.5 Sonnet Pricing**
- **Input tokens**: ~$3.00 per 1M tokens
- **Output tokens**: ~$15.00 per 1M tokens
- **Typical essay grading**: ~$0.02-0.03 per essay

#### **Cost Protection Features**
- **Rate Limiting**: 20 requests/minute, 50 essays/hour
- **Daily Limits**: 100 essays/day, 50,000 words/day
- **Usage Tracking**: Real-time monitoring via `/usage/summary`
- **Teacher-Friendly**: Generous limits with clear error messages




### **Security Considerations**

#### **API Key Protection**
- **Never commit API keys** to version control
- **Use environment variables** for all secrets

#### **Rate Limiting**
- **Built-in protection** against abuse
- **Teacher-appropriate limits** (100 essays/day)
- **Clear error messages** when limits exceeded

#### **Network Security**
```bash
# Production environment variables
ALLOWED_ORIGINS=https://your-frontend-domain.com
CORS_CREDENTIALS=true
DEBUG=false
```

## Important Notes
- **Primary Development**: Focus on Python backend in `/backend/` directory
- **Production Ready**: Backend now includes rate limiting, structured logging, usage safeguards, and monitoring
- **AI Configuration**: Use mock mode for development, real AI for production (see AI Configuration above)
- **Testing**: Run `pytest tests/ -v` for comprehensive test suite (320+ tests)
- **API Documentation**: Available at http://localhost:8000/docs when server is running
- **Monitoring**: Use /health/detailed and /usage/summary for operational visibility
- **Cost Protection**: Daily limits prevent excessive Anthropic API usage
- **Clean Architecture**: APUSHGraderCore completely removed, Python backend is single source of truth
