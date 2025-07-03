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
**Phase 2C READY**: Testing and documentation updates
**Legacy**: Swift Package (APUSHGraderCore) will be replaced by Python backend

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

### **APUSHGraderCore/** - Swift Package (LEGACY - Being Replaced)
- Complete Swift implementation with 223 tests
- Will be replaced by Python backend in Phase 3

### **APUSHGrader/** - iOS App (UI Layer - Future API Integration)
- Current: Uses APUSHGraderCore locally  
- Future: Will use Python backend via HTTP API

## Python Backend Commands

### **Development Environment Setup**
```bash
cd backend
source venv/bin/activate              # Activate Python virtual environment
pip install -r requirements.txt       # Install core dependencies  
pip install -r requirements-dev.txt   # Install development tools
```

### **Running the Server**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload         # Development server with auto-reload
uvicorn app.main:app --reload --port 8001  # Use different port if needed
```

### **Testing**
```bash
cd backend
source venv/bin/activate
pytest tests/ -v                      # Run all tests with verbose output
pytest tests/integration/ -v          # Run integration tests only
pytest tests/services/processing/prompt/ -v  # Run prompt generation tests only
pytest tests/ --tb=short              # Run with short traceback format
```

### **API Testing**
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health
- **Detailed Health**: http://localhost:8000/health/detailed
- **Usage Summary**: http://localhost:8000/usage/summary
- **Grade Endpoint**: POST http://localhost:8000/api/v1/grade (rate limited)

## Legacy Swift Commands (For Reference)
- **iOS App**: ⌘+B in Xcode, ⌘+R to run
- **Swift Package Testing**: `swift run TestRunner` (from APUSHGraderCore/)

## Testing Status

### **Python Backend Testing (PRODUCTION READY)**
✅ **320+ Comprehensive Tests** - All passing with full coverage
- **19 PromptGenerator Tests** - Essay-specific prompt generation and validation
- **49 Integration Tests** - End-to-end API workflow + production features testing  
- **69 Response Processing Tests** - AI response processing services
- **94 Core Processing Tests** - Essay validation, text analysis, warning generation
- **88+ Model Tests** - Data model validation and business logic
- **Production Feature Tests** - Rate limiting, structured logging, usage safeguards, health monitoring

### **Legacy Swift Testing**
✅ **223 Swift Tests** - Original implementation (will be replaced)
- Custom TestRunner framework with modular organization
- All Swift business logic successfully migrated to Python

## Essay Types Supported
- **DBQ** (Document-Based Question) - 6 points
- **LEQ** (Long Essay Question) - 6 points  
- **SAQ** (Short Answer Question) - 3 points

## Current Status - Phase 2B COMPLETE ✅

### **✅ Python Backend (PRODUCTION READY)**
- **Complete FastAPI Backend** - Full grading workflow with 320+ passing tests
- **Production Features** - Rate limiting, structured logging, usage safeguards, health monitoring
- **API Endpoints** - POST /api/v1/grade (rate limited), health endpoints, usage monitoring
- **Real & Mock AI Integration** - Configurable Anthropic Claude 3.5 Sonnet or mock responses
- **Service Architecture** - Clean dependency injection with protocol-based interfaces
- **Comprehensive Testing** - End-to-end integration tests covering complete workflows and production features

### **✅ Migration Milestones Completed**
- **Phase 1A Complete** - Python FastAPI project structure and foundation
- **Phase 1B Complete** - Swift models migration to Python (88 tests)
- **Phase 1C-1 Complete** - Core processing services (essay validation, text analysis)
- **Phase 1C-2 Complete** - Response processing services (validation, insights, formatting)
- **Phase 1C-3 Complete** - Prompt generation & complete API integration (34 tests)
- **Phase 2A Complete** - Real Anthropic AI service integration implemented
- **Phase 2B Complete** - Production readiness (rate limiting, logging, usage safeguards, monitoring)

### **📋 Next Phases**
- **Phase 2C Ready** - Testing and documentation updates
- **Phase 3 Ready** - Migrate iOS frontend to use Python backend API  
- **Phase 4 Ready** - Production deployment and monitoring
- **Legacy iOS** - Still uses APUSHGraderCore locally, will migrate to HTTP API in Phase 3

### **🔧 Development Environment**
- **AI Service Configuration**: Switch between mock and real AI (see AI Configuration section below)
- **API Keys**: Anthropic API key required for real AI integration
- **Server**: `uvicorn app.main:app --reload` for development
- **Testing**: `pytest tests/ -v` for comprehensive test suite

## Migration Progress

**Current Status**: Phase 2B COMPLETE ✅ - Production readiness implemented with rate limiting, logging, usage safeguards, and monitoring

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
- **Phase 2C**: Testing and documentation updates (optional)
- **Phase 3**: Migrate iOS frontend to use Python backend API  
- **Phase 4**: Production deployment and monitoring

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
- **Anthropic AI**: Uses Claude 3.5 Sonnet model with temperature=0.3, max_tokens=1500
- **Seamless Switching**: Same API interface works with both mock and real AI
- **Error Handling**: Graceful fallback and user-friendly error messages
- **Testing**: All existing tests work with both AI service types

## Important Notes
- **Primary Development**: Focus on Python backend in `/backend/` directory
- **Production Ready**: Backend now includes rate limiting, structured logging, usage safeguards, and monitoring
- **AI Configuration**: Use mock mode for development, real AI for production (see AI Configuration above)
- **Testing**: Run `pytest tests/ -v` for comprehensive test suite (320+ tests)
- **API Documentation**: Available at http://localhost:8000/docs when server is running
- **Monitoring**: Use /health/detailed and /usage/summary for operational visibility
- **Cost Protection**: Daily limits prevent excessive Anthropic API usage
- **Legacy Swift**: APUSHGraderCore still functional but will be replaced by backend API
