# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
APUSH Grader - Migrating from iOS SwiftUI app to **Python FastAPI backend + iOS frontend** architecture. Uses AI (OpenAI/Anthropic) to grade AP US History essays based on College Board rubrics.

## Current Architecture Status
**Phase 1 COMPLETE**: Python backend with comprehensive API and testing
**Phase 2 READY**: Real AI service integration needed
**Legacy**: Swift Package (APUSHGraderCore) will be replaced by Python backend

## Repository Structure

### **backend/** - Python FastAPI Backend (ACTIVE DEVELOPMENT)
- **app/main.py** - FastAPI application entry point
- **app/api/routes/** - API endpoints
  - **grading.py** - POST /api/v1/grade endpoint (complete workflow)
  - **health.py** - Health check endpoints
- **app/models/** - Pydantic data models
  - **core/** - Core business models (essay_types, grade_models, api_models)
  - **processing/** - Processing models (response, display, preprocessing)
  - **requests/** - API request/response models (grading, health)
- **app/services/** - Business logic services
  - **api/coordinator.py** - End-to-end workflow orchestration
  - **processing/essay/** - Essay processing (validator, analyzer, cleaner, warnings)
  - **processing/prompt/generator.py** - Essay-specific AI prompt generation
  - **processing/response/** - AI response processing (validator, insights, formatter)
  - **dependencies/service_locator.py** - Dependency injection container
- **tests/** - Comprehensive test suite (285+ tests)
  - **integration/** - End-to-end workflow tests
  - **services/processing/prompt/** - Prompt generation tests
  - All other test suites for models and services
- **requirements.txt** - Core dependencies (FastAPI, Pydantic, uvicorn)
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
- **Grade Endpoint**: POST http://localhost:8000/api/v1/grade

## Legacy Swift Commands (For Reference)
- **iOS App**: ⌘+B in Xcode, ⌘+R to run
- **Swift Package Testing**: `swift run TestRunner` (from APUSHGraderCore/)

## Testing Status

### **Python Backend Testing (ACTIVE)**
✅ **285+ Comprehensive Tests** - All passing with full coverage
- **19 PromptGenerator Tests** - Essay-specific prompt generation and validation
- **15 Integration Tests** - End-to-end API workflow testing  
- **69 Response Processing Tests** - AI response processing services
- **94 Core Processing Tests** - Essay validation, text analysis, warning generation
- **88+ Model Tests** - Data model validation and business logic

### **Legacy Swift Testing**
✅ **223 Swift Tests** - Original implementation (will be replaced)
- Custom TestRunner framework with modular organization
- All Swift business logic successfully migrated to Python

## Essay Types Supported
- **DBQ** (Document-Based Question) - 6 points
- **LEQ** (Long Essay Question) - 6 points  
- **SAQ** (Short Answer Question) - 3 points

## Current Status - Phase 1 COMPLETE

### **✅ Python Backend (PRODUCTION READY)**
- **Complete FastAPI Backend** - Full grading workflow with 285+ passing tests
- **API Endpoints** - POST /api/v1/grade and GET /api/v1/grade/status fully functional
- **Mock AI Integration** - Realistic responses for all essay types (no external API calls)
- **Service Architecture** - Clean dependency injection with protocol-based interfaces
- **Comprehensive Testing** - End-to-end integration tests covering complete workflows

### **✅ Phase 1 Migration Milestones**
- **Phase 1A Complete** - Python FastAPI project structure and foundation
- **Phase 1B Complete** - Swift models migration to Python (88 tests)
- **Phase 1C-1 Complete** - Core processing services (essay validation, text analysis)
- **Phase 1C-2 Complete** - Response processing services (validation, insights, formatting)
- **Phase 1C-3 Complete** - Prompt generation & complete API integration (34 tests)

### **📋 Next Phase Ready**
- **Phase 2 Ready** - Real AI service integration (OpenAI/Anthropic) to replace mock responses
- **Legacy iOS** - Still uses APUSHGraderCore locally, will migrate to HTTP API in Phase 3

### **🔧 Development Environment**
- **API Keys**: Configured in backend environment for future real AI integration
- **Mock Mode**: Currently using realistic mock AI responses for testing
- **Server**: `uvicorn app.main:app --reload` for development
- **Testing**: `pytest tests/ -v` for comprehensive test suite

## Migration Progress

**Current Status**: Phase 1 COMPLETE ✅ - Python backend ready for Phase 2 real AI integration

### **Target Architecture (ACHIEVED)**
```
iOS Frontend (SwiftUI) → HTTP API → Python Backend (FastAPI) → Mock AI (Phase 1) / Real AI (Phase 2)
```

### **Next Steps**
- **Phase 2**: Replace mock AI responses with real OpenAI/Anthropic API integration
- **Phase 3**: Migrate iOS frontend to use Python backend API  
- **Phase 4**: Production deployment and monitoring

**See PLAN.md for detailed migration timeline and implementation details.**

## Architecture Benefits
- **Clean Service Architecture**: Protocol-based dependency injection with service locator pattern
- **Comprehensive Testing**: 285+ tests covering all components with mock AI integration
- **Platform-Agnostic Design**: Backend ready for multiple frontends (iOS, web, etc.)
- **Production Ready**: Complete API with error handling, validation, and monitoring
- **Maintainable Codebase**: Python ecosystem easier than complex Swift/iOS
- **Scalable Design**: Easy to add new features without affecting existing components

## Important Notes
- **Primary Development**: Focus on Python backend in `/backend/` directory
- **Mock AI Mode**: Currently using realistic mock responses (no external API calls)
- **Testing**: Run `pytest tests/ -v` for comprehensive test suite
- **API Documentation**: Available at http://localhost:8000/docs when server is running
- **Legacy Swift**: APUSHGraderCore still functional but will be replaced by backend API
