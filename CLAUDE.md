# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
APUSH Grader - iOS SwiftUI app that uses AI (OpenAI/Anthropic) to grade AP US History essays based on College Board rubrics.

## Repository Architecture - Hybrid SPM/iOS Structure
The project uses a **hybrid architecture** with business logic in a Swift Package and UI in the iOS app:

### **APUSHGraderCore/** - Swift Package (Business Logic)
- **Package.swift** - SPM configuration for iOS 16+, includes TestRunner executable
- **Sources/APUSHGraderCore/**
  - **Models/Core/** - Core data models (all public)
    - **EssayType.swift** - Essay type enum with UI properties and scoring rules
    - **GradeModels.swift** - Core grading structures (GradeResponse, RubricItem, etc.)
    - **APIModels.swift** - API configuration and model definitions
  - **Models/Processing/** - Processing data models  
    - **PreprocessingModels.swift** - Text processing result structures
  - **Services/API/** - API service implementations (all public)
    - **APIServiceProtocol.swift** - Service interface definitions
    - **APIService.swift** - Main coordinator with retry logic
    - **OpenAIService.swift** - OpenAI-specific implementation
    - **AnthropicService.swift** - Anthropic-specific implementation  
    - **MockAPIService.swift** - Testing implementation
  - **Services/Processing/** - Business logic processing (all public)
    - **EssayProcessing/** - Text preprocessing and validation (EssayValidator, TextAnalyzer, TextCleaner, WarningGenerator)
    - **ResponseProcessing/** - AI response processing  
    - **PromptGeneration/** - AI prompt generation
- **Sources/TestRunner/** - Modular test suite executable
  - **TestFramework.swift** - Custom testing framework for SPM
  - **Tests/** - Individual test suite files
  - **main.swift** - Test coordinator

### **APUSHGrader/** - iOS App (UI Layer)
- **Views/** - SwiftUI views (import APUSHGraderCore)
  - **Main/ContentView.swift** - Main app coordinator
  - **Main/GradeResultsView.swift** - Detailed results display
  - **Components/** - Reusable UI components
- **App/** - Application configuration
  - **APUSHGraderApp.swift** - App entry point (cleaned up)
  - **Info.plist** - API keys and app configuration
- **Resources/** - Assets and preview content
- **Utilities/** - Empty directories for future extensions/helpers

## Development Commands
- **iOS App**: ⌘+B in Xcode, ⌘+R to run, Product → Clean Build Folder
- **Swift Package Testing**: `swift run TestRunner` (custom modular test suite)
- **Swift Package Build**: `cd APUSHGraderCore && swift build` (command line)

## Testing

### **Modular TestRunner Architecture** 
✅ **Custom SPM Testing Framework** - No XCTest dependencies, pure Swift Package Manager approach
✅ **223 Comprehensive Tests** - Covering all core business logic with zero failures
✅ **Modular Test Organization** - Separate test files per source file for maintainability
✅ **Terminal-Based Testing** - Run with `swift run TestRunner` for rapid iteration

### **Completed Test Suites**
✅ **EssayTypeTests** (48 tests) - Essay scoring rules, rubric structures, UI properties
✅ **GradeModelsTests** (35 tests) - Grade calculations, letter grades, performance levels  
✅ **APIModelsTests** (38 tests) - API configurations, model mappings, validation ranges
✅ **PreprocessingModelsTests** (32 tests) - Text processing validation, critical warning detection
✅ **EssayProcessingTests** (70 tests) - Text analysis, content detection, essay validation

### **Remaining Test Priorities**
📋 **ResponseProcessingTests** (medium priority) - AI response processing services
  - ResponseProcessor, ResponseValidator, InsightsGenerator, ResponseFormatter, ErrorPresentation
📋 **PromptGenerationTests** (low priority) - Essay-specific prompt generation
  - PromptGenerator for DBQ/LEQ/SAQ specific prompts

### **Validated Business Logic** 
✅ **Essay Type Rules** - DBQ/LEQ (6 pts, 400+/300+ words), SAQ (3 pts, 50+ words)
✅ **Validation Thresholds** - Minimum: DBQ 200+, LEQ 150+, SAQ 25+ words
✅ **Maximum Limits** - DBQ 2400, LEQ 2000, SAQ 600 words
✅ **Content Analysis** - Thesis detection, evidence keywords, informal language detection
✅ **Text Processing** - Word/paragraph counting, Unicode normalization, whitespace handling
✅ **Warning System** - Critical warnings ("too short"/"too long") vs advisory warnings
✅ **Grade Calculations** - Percentage/letter grade mappings, performance level classification

### **Test Configuration**
- **Run Tests**: `swift run TestRunner` (from APUSHGraderCore/ directory)
- **Test Framework**: Custom modular approach with TestSuite classes and TestRunnable protocol
- **Public APIs**: All business logic classes made public for comprehensive testing
- **Mock API**: Use `MockAPIService()` in Views/Main/ContentView.swift line 13-14
- **Real AI**: Use `APIService()` in Views/Main/ContentView.swift line 13-14  
- **API Keys**: Stored in App/Info.plist (OPENAI_API_KEY, ANTHROPIC_API_KEY)

## Essay Types Supported
- **DBQ** (Document-Based Question) - 6 points
- **LEQ** (Long Essay Question) - 6 points  
- **SAQ** (Short Answer Question) - 3 points

## Current Status
✅ **Hybrid SPM/iOS architecture successfully implemented**
✅ **Business logic extracted to Swift Package** - APUSHGraderCore with public APIs
✅ **iOS app builds and runs** - Proper import of APUSHGraderCore 
✅ **SwiftUI previews working** - UI development capabilities preserved
✅ **Comprehensive test suite complete** - 223 tests covering all core business logic
✅ **Modular TestRunner architecture** - Custom SPM testing framework, no XCTest dependencies
✅ Fully functional with mock API
✅ Real API keys configured in Info.plist
✅ Prompt input feature - users can enter the specific question/prompt
✅ UI flow: Essay Type → Prompt Input → Essay Text → Grade Button
✅ **Core business logic fully validated** - Essay processing, text analysis, grading calculations
✅ **Python Backend Foundation Complete** - FastAPI server with models, services, and testing
✅ **Phase 1C-1 Complete** - Service architecture and core processing services implemented
✅ **Phase 1C-2 Complete** - AI response processing services with platform-agnostic design
📋 **Phase 1C-3 Pending** - Prompt generation & complete API integration (GitHub Issue #5)
⚠️ **NOT YET TESTED** with actual AI APIs (OpenAI/Anthropic)
✅ Scrollable UI with detailed breakdown

## Migration Plan: iOS Frontend + Python Backend

**Status**: Phase 1C-2 complete, Phase 1C-3 (Prompt Generation & API Integration) needed before Phase 2

### **Migration Rationale**
Current Swift implementation is excellently architected but over-engineered for hobby project scope. Migration to Python backend provides:
- **Better Maintainability**: Python ecosystem easier than complex Swift/iOS
- **Universal Access**: Future web frontend expansion
- **Simplified Deployment**: Standard web hosting vs App Store complexity  
- **Preserved UI**: Keep polished SwiftUI interface

### **Target Architecture**
```
iOS Frontend (Swift/SwiftUI) → HTTP API → Python Backend (FastAPI) → AI APIs
```

**Frontend (Keep in iOS)**:
- SwiftUI views and UI components
- User input handling and navigation  
- HTTP client with simple models
- Display formatting and animations

**Backend (Move to Python)**:
- All APUSHGraderCore business logic
- AI service integrations (OpenAI/Anthropic)
- Essay processing, validation, scoring
- Prompt generation and response processing

### **Migration Timeline**

**Phase 1: Backend Foundation**
- Python FastAPI project setup with models
- Migrate core business logic from Swift
- Comprehensive test suite (preserve 223 tests)
- Health check and validation endpoints

**Phase 2: API Development**  
- REST API endpoints (`POST /grade`, `GET /health`)
- AI service integration (OpenAI/Anthropic)
- Error handling and retry logic
- API documentation with OpenAPI/Swagger

**Phase 3: iOS Migration**
- Create HTTP client layer in iOS
- Simplify models to DTOs only
- Update ContentView and GradeResultsView
- Remove APUSHGraderCore dependencies

**Phase 4: Testing & Deployment**
- End-to-end integration testing
- Deploy to Railway hosting ($5-6/month)
- User acceptance testing
- Legacy code cleanup

### **Technology Stack**
- **Backend**: FastAPI + Pydantic + httpx
- **Testing**: pytest + comprehensive test suite
- **Deployment**: Railway hosting with automatic deployments
- **Monitoring**: Sentry (free tier) + built-in platform monitoring
- **Database**: Stateless initially, PostgreSQL if needed later

### **API Contract**
```json
POST /api/v1/grade
{
  "essay_text": "string",
  "essay_type": "DBQ|LEQ|SAQ", 
  "prompt": "string"
}

Response: {
  "score": 5, "max_score": 6,
  "breakdown": {...}, "feedback": "...",
  "suggestions": [...], "warnings": [...]
}
```


### **Migration Commands**
- **Python Backend**: `uvicorn main:app --reload` (development)
- **Testing**: `pytest` (comprehensive test suite)
- **Deployment**: Git push triggers auto-deploy to Railway
- **iOS Changes**: Update imports, add NetworkService, simplify models

## Migration Progress Status

**See PLAN.md for detailed migration timeline, progress tracking, and implementation details.**

### **Development Environment Setup**
For Phase 1C-2 development:
```bash
cd backend
source venv/bin/activate              # Activate Python environment
pip install -r requirements.txt       # Core dependencies  
pip install -r requirements-dev.txt   # Development tools
uvicorn app.main:app --reload         # Start development server
pytest tests/ -v                      # Run tests with verbose output
```

**Decision**: Migration recommended for better maintainability and future scalability while preserving excellent UI and business logic.

## Architecture Benefits
- **Hybrid Structure**: Best of both worlds - SPM testing + iOS capabilities
- **Clean Module Boundaries**: Business logic separate from UI layer
- **Custom Test Framework**: Terminal-based testing with `swift run TestRunner` for rapid iteration
- **iOS Development Preserved**: Xcode previews, App Store deployment, Info.plist
- **Public API Design**: Forced clean interfaces between modules, all business logic publicly testable
- **Modular Testing**: Each test suite focuses on one source file for maintainability
- **Single Responsibility**: Each file has one clear purpose  
- **Comprehensive Coverage**: 223 tests validating all core business logic
- **Maintainability**: Easy to find and modify specific functionality
- **Reusability**: UI components can be used across different views
- **Scalability**: Easy to add new test suites and features without affecting existing code

## Common Issues
- **SPM Access Control**: All types used by iOS app must be `public` in APUSHGraderCore
- **Missing Initializers**: Add `public init(...)` for structs used in iOS app
- **Testing Public APIs**: All classes intended for testing must be `public` (EssayValidator, TextAnalyzer, etc.)
- Multi-line strings must start content on new line after `"""`
- Info.plist conflicts: Use `GENERATE_INFOPLIST_FILE = NO`
- Unicode characters in strings: Use escape sequences like `\u{201C}`
- When adding new UI components, place them in APUSHGrader/Views/Components/
- When adding new business logic, place them in APUSHGraderCore/Sources/APUSHGraderCore/
- When adding new tests, create new test files in Sources/TestRunner/Tests/ and add to main.swift coordinator

## Python Backend Structure (Migration Target)

### **backend/** - Python FastAPI Backend
- **app/models/core/** - Core data models (Pydantic)
  - **essay_types.py** - Essay type enum with scoring rules
  - **grade_models.py** - Grade response and rubric structures  
  - **api_models.py** - API configuration models
- **app/models/processing/** - Processing data models
  - **response.py** - Response processing models (ProcessedGradingResult, GradingInsight, ValidationResult)
  - **display.py** - Platform-agnostic display models (DisplayColors, DisplayConstants)
- **app/services/processing/essay/** - Essay processing services
  - **processor.py, validator.py, analyzer.py, cleaner.py, warnings.py** - Core essay processing
- **app/services/processing/response/** - Response processing services (Phase 1C-2)
  - **processor.py** - Main response coordinator 
  - **validator.py** - Score validation and consistency checks
  - **insights.py** - Performance analysis and essay-specific tips
  - **formatter.py** - Platform-agnostic markdown formatting
  - **errors.py** - User-friendly error message mapping
- **app/services/dependencies/** - Dependency injection
  - **service_locator.py** - Service locator with protocol-based DI
- **tests/** - Comprehensive Python test suite
  - **tests/services/processing/response/** - 69 response processing tests (Phase 1C-2)
