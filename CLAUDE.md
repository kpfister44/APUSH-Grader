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
  - **health.py** - Health check endpoints (/health, /usage/summary)
- **app/middleware/** - Rate limiting middleware
  - **rate_limiting.py** - SlowAPI rate limiting (20 req/min, 50 essays/hour)
- **app/models/** - Simplified Pydantic data models
  - **core.py** - Consolidated core models (EssayType, GradeResponse, RubricItem, Provider, Model)
  - **processing.py** - Simplified processing models (PreprocessingResult, GradingInsight, ValidationResult)
  - **requests/** - API request/response models (grading, health)
- **app/services/** - Business logic services
  - **api/coordinator.py** - End-to-end workflow orchestration
  - **processing/essay/** - Essay processing (validator, analyzer, cleaner, warnings)
  - **processing/prompt/generator.py** - Essay-specific AI prompt generation
  - **processing/response/** - AI response processing (validator, insights, formatter)
  - **dependencies/service_locator.py** - Dependency injection container
- **app/utils/** - Simple utility functions
  - **simple_usage.py** - Basic daily usage tracking (50 essays/day limit)
- **tests/** - Simplified test suite (51 tests)
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

### **Manual Essay Testing**
For testing real essays and evaluating grading quality, use the manual essay testing script:

```bash
# Ensure you're in backend directory with virtual environment activated
cd backend
source venv/bin/activate

# Quick test with sample essays (for testing the system)
python manual_essay_tester.py --sample dbq    # Test with sample DBQ essay
python manual_essay_tester.py --sample leq    # Test with sample LEQ essay
python manual_essay_tester.py --sample saq    # Test with sample SAQ essay

# Test with your own essay files
python manual_essay_tester.py my_essay.txt dbq my_prompt.txt

# Interactive mode - enter essay and prompt manually
python manual_essay_tester.py
```

**Sample Essay Files**: The script uses text files in `/backend/sample_essays/` directory:
- `dbq_essay.txt`, `leq_essay.txt`, `saq_essay.txt` - Sample essays (replace with real content)
- `saq_stimulus_essay.txt`, `saq_non_stimulus_essay.txt`, `saq_secondary_comparison_essay.txt` - SAQ type-specific essays
- `prompts/dbq_prompt.txt`, `prompts/leq_prompt.txt`, `prompts/saq_prompt.txt` - Sample prompts
- `prompts/saq_stimulus_prompt.txt`, `prompts/saq_non_stimulus_prompt.txt`, `prompts/saq_secondary_comparison_prompt.txt` - SAQ type-specific prompts

**Output**: The script displays detailed grading results including:
- Overall score and letter grade
- Breakdown by rubric categories with individual scores and feedback
- Overall feedback from AI
- Specific suggestions for improvement

**AI Service**: 
- Uses mock AI by default (no API key required)
- Set `ANTHROPIC_API_KEY` environment variable to use real AI grading
- Real AI costs ~$0.02-0.03 per essay

**SAQ Type Testing**: Test specific SAQ types with type differentiation:
```bash
# Test different SAQ types with simplified syntax
python manual_essay_tester.py --sample saq stimulus           # Test stimulus SAQ
python manual_essay_tester.py --sample saq non_stimulus       # Test non-stimulus SAQ
python manual_essay_tester.py --sample saq secondary_comparison # Test secondary comparison SAQ

# Test different SAQ types with specific files
python manual_essay_tester.py sample_essays/saq_stimulus_essay.txt saq sample_essays/prompts/saq_stimulus_prompt.txt
python manual_essay_tester.py sample_essays/saq_non_stimulus_essay.txt saq sample_essays/prompts/saq_non_stimulus_prompt.txt
python manual_essay_tester.py sample_essays/saq_secondary_comparison_essay.txt saq sample_essays/prompts/saq_secondary_comparison_prompt.txt
```

### **API Testing**
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health
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
✅ **51 Simplified Tests** - All passing with focused coverage
- **10 Core Workflow Tests** - Essential grading workflow and validation
- **13 Integration Tests** - End-to-end API workflow + production features testing  
- **23 Utility Tests** - Essay processing, prompt generation, response processing
- **5 Health/Monitoring Tests** - Rate limiting, usage tracking, health monitoring

### **iOS App Testing**
✅ **SwiftUI Integration** - iOS app successfully connects to Python backend
- NetworkService handles HTTP API communication
- Real-time testing possible via SwiftUI previews
- All business logic now handled by Python backend API

## Essay Types Supported
- **DBQ** (Document-Based Question) - 6 points
- **LEQ** (Long Essay Question) - 6 points  
- **SAQ** (Short Answer Question) - 3 points with **type differentiation**:
  - **Stimulus SAQ** - Uses primary/secondary source document for analysis
  - **Non-Stimulus SAQ** - Pure text-based questions without accompanying sources
  - **Secondary Stimulus Comparison SAQ** - Compares contrasting historical interpretations

### **SAQ Type Differentiation**
The backend and frontend now support specialized grading for different SAQ types with type-specific AI prompts:
- **Stimulus SAQ**: Evaluates source analysis skills and contextualization
- **Non-Stimulus SAQ**: Focuses on historical content knowledge and evidence quality
- **Secondary Comparison SAQ**: Assesses historiographical understanding and interpretation analysis

### **iOS Frontend SAQ Type Selection**
The iOS app now includes SAQ type selection UI for improved grading accuracy:
- **Optional Dropdown**: Appears only when SAQ essay type is selected
- **User-Friendly Labels**: "Source Analysis", "Content Question", "Historical Comparison"
- **Backward Compatible**: Existing SAQ submissions work without type selection
- **State Management**: SAQ type selection resets when essay type changes

## Current Status - Backend Simplification COMPLETE ✅

### **✅ Python Backend (PRODUCTION READY + FULLY SIMPLIFIED)**
- **Complete FastAPI Backend** - Full grading workflow with simplified architecture
- **Simplified Infrastructure** - Rate limiting, basic logging, simple usage tracking (93% complexity reduction)
- **Consolidated Models** - Core models unified with proper SAQ/DBQ/LEQ support + SAQ type differentiation (55% complexity reduction)
- **API Endpoints** - POST /api/v1/grade (rate limited), /health, /usage/summary
- **Real AI Integration** - Anthropic Claude 3.5 Sonnet with comprehensive testing
- **Simplified Service Architecture** - Direct utility functions replacing complex dependency injection (75% complexity reduction)
- **Testing Coverage** - All integration tests passing, comprehensive coverage of core functionality
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

### **✅ Backend Simplification Milestones Completed**
- **Phase 1 Infrastructure Simplification Complete** - Removed complex logging/monitoring, simplified usage tracking (93% reduction)
- **Phase 2 Model Consolidation Complete** - Unified core models, proper SAQ/DBQ/LEQ support (55% reduction)
- **Phase 3 Service Architecture Simplification Complete** - Replaced dependency injection with utility functions (75% reduction)
- **Phase 4 Test Suite Optimization Complete** - Fixed integration tests, removed complex infrastructure tests
- **Phase 5 Final Cleanup Complete** - All tests passing, simplified exceptions handling

### **🔧 Development Environment**
- **AI Service Configuration**: Switch between mock and real AI (see AI Configuration section below)
- **API Keys**: Anthropic API key required for real AI integration
- **Server**: `uvicorn app.main:app --reload` for development
- **Testing**: `pytest tests/ -v` for comprehensive test suite

## Migration Progress

**Current Status**: Backend Simplification COMPLETE ✅ - All 5 phases implemented with 87% overall complexity reduction

### **Target Architecture (ACHIEVED)**
```
iOS Frontend (SwiftUI) → HTTP API → Python Backend (FastAPI) → Mock AI / Real Anthropic AI (configurable)
                                      ↓
                              Simplified Features (87% complexity reduction):
                              • Rate Limiting (20 req/min, 50 essays/hour)
                              • Basic Python Logging (replaced structured logging)
                              • Simple Usage Limits (50 essays/day)
                              • Utility-based Processing (replaced service architecture)
                              • Essential Test Coverage (51 tests, focused on business logic)
                              • Health Monitoring (/health, /usage/summary)
```

### **🎯 Production Ready**
The backend has been fully simplified and is ready for production deployment with:
- **Complete Functionality**: All grading workflows work with simplified architecture
- **Essential Test Coverage**: 51 focused tests covering core business logic
- **Clean Codebase**: 87% complexity reduction makes maintenance simple
- **Cost Protection**: Built-in rate limiting and usage safeguards
- **Easy Deployment**: Straightforward architecture suitable for hobby project scale

### **🚀 Future Production Steps**
- **Production Deployment**: Simplified architecture deployment
- **Web Frontend**: Optional expansion for additional platforms

**See PLAN.md for detailed migration timeline and implementation details.**

## Architecture Benefits After Simplification
- **Hobby Project Appropriate**: Simplified architecture suitable for 2-12 teachers (not enterprise scale)
- **Reduced Complexity**: 93% infrastructure reduction + 55% model consolidation
- **Maintainable Codebase**: Much simpler Python codebase with direct imports and flat structure
- **Platform-Agnostic Design**: Backend ready for multiple frontends (iOS, web, etc.)
- **Essential Features Only**: Rate limiting, basic logging, simple usage tracking
- **Cost Protection**: Appropriate daily limits (50 essays/day) to prevent excessive Anthropic API costs
- **Teacher-Friendly**: Clear error messages and reasonable limits for small user base
- **Development Velocity**: Faster development with reduced abstraction layers
- **Easy Onboarding**: Simple structure for new developers to understand

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
- **Daily Limits**: 50 essays/day, 10,000 words/essay
- **Usage Tracking**: Simple daily counter via `/usage/summary`
- **Teacher-Friendly**: Appropriate limits with clear error messages




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
- **Simplified Architecture**: Backend uses basic logging, simple usage tracking, consolidated models
- **Ongoing Simplification**: Currently in Phase 2 complete, Phase 3-4 planned for service/test simplification
- **AI Configuration**: Use mock mode for development, real AI for production (see AI Configuration above)
- **Testing**: Run `pytest tests/ -v` for simplified test suite (51 tests, focused on core business logic)
- **API Documentation**: Available at http://localhost:8000/docs when server is running
- **Monitoring**: Use /health and /usage/summary for basic operational visibility
- **Cost Protection**: Daily limits prevent excessive Anthropic API usage (50 essays/day)
- **Clean Architecture**: APUSHGraderCore completely removed, Python backend is single source of truth
- **Hobby Project Scale**: Infrastructure simplified for 2-12 teacher usage, not enterprise scale
- **Model Structure**: Consolidated to 3 files (core.py, processing.py, requests/) vs original 12 files
- **SAQ Type Differentiation**: Backend supports specialized grading for stimulus, non-stimulus, and secondary comparison SAQs
