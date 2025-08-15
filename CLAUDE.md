# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
APUSH Grader - Multi-platform AI essay grading system with **Python FastAPI backend + iOS SwiftUI + ChatGPT-style web frontend**. Uses Anthropic Claude to grade AP US History essays (DBQ/LEQ/SAQ) based on College Board rubrics.

## Target Audience and Scope
Designed for 2-12 teachers. Prioritize simplicity over complexity - functionality over comprehensiveness. Not meant for enterprise scale.

## Current Status
- **Backend**: Production-ready Python FastAPI with Anthropic AI integration ✅
- **iOS App**: Complete, using backend API ✅
- **Web Frontend**: Phase 4 cross-browser testing complete, ready for Issue #38 (production deployment)

## Tech Stack

### **Backend (Python)**
- **Framework**: FastAPI 0.104.1 - Modern, fast web framework with automatic API docs
- **Server**: Uvicorn 0.24.0 - Lightning-fast ASGI server  
- **Data Validation**: Pydantic 2.5.0 + Pydantic Settings 2.1.0 - Type-safe data models
- **Environment**: Python-dotenv 1.0.0 - Environment variable management
- **AI Integration**: Anthropic 0.57.1 - Claude API client
- **Rate Limiting**: SlowAPI 0.1.9 - Request throttling and protection
- **Language**: Python 3.12

### **Web Frontend (React/TypeScript)**
- **Framework**: React 19.1.0 + React DOM 19.1.0 - Modern component-based UI
- **Routing**: React Router DOM 7.7.0 - Client-side navigation
- **Styling**: Tailwind CSS 4.1.11 - Utility-first CSS framework
- **Build Tool**: ESBuild 0.25.8 - Fast bundler and dev server
- **Language**: TypeScript 5.8.3 - Type-safe JavaScript
- **PDF Export**: @react-pdf/renderer 4.3.0 - Client-side PDF generation
- **Dev Workflow**: Hot reloading, CSS watching, parallel builds

### **iOS App (Swift/SwiftUI)**
- **Framework**: SwiftUI - Declarative UI framework
- **Language**: Swift - Native iOS development
- **Architecture**: MVVM pattern with API integration
- **Network**: URLSession-based HTTP client for backend API

### **Development Tools**
- **API Documentation**: FastAPI automatic OpenAPI/Swagger docs
- **Testing**: Pytest (51 tests for backend)
- **Version Control**: Git with feature branch workflow
- **CI/CD**: GitHub Actions ready
- **Environment**: Multi-platform (macOS, iOS, Web)

## Repository Structure

### **backend/** - Python FastAPI Backend (PRODUCTION READY)
- **app/main.py** - FastAPI application entry point
- **app/api/routes/** - API endpoints (grading.py, health.py)
- **app/models/** - Pydantic data models (core.py, processing.py, requests/)  
- **app/services/** - Business logic services (coordinator, essay processing, prompt generation)
- **tests/** - 51 focused tests covering core functionality
- **requirements.txt** - Core dependencies (FastAPI, Pydantic, uvicorn, anthropic, slowapi)

### **APUSHGrader/** - iOS App
- **Models/** - API DTOs matching Python backend
- **Services/NetworkService.swift** - HTTP client for backend API
- **Views/** - SwiftUI interface using API responses
- Uses Python backend via HTTP API (localhost:8000)

### **webfrontend/** - ChatGPT-Style Web Frontend
- **src/components/** - React UI components with ChatGPT-inspired design
  - **pdf/** - PDF export functionality using @react-pdf/renderer
- **src/contexts/** - React Context for state management  
- **src/services/** - API client service for backend integration
- **src/types/** - TypeScript interface definitions
- Phase 4 cross-browser testing complete, PDF export feature added, ready for Issue #38 (production deployment)

## Commands

### **Python Backend**
```bash
# Setup
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run server
uvicorn app.main:app --reload
# Available at: http://localhost:8000, docs at /docs

# Testing
pytest tests/ -v

# Manual essay testing
python manual_essay_tester.py --sample dbq
python manual_essay_tester.py --sample leq  
python manual_essay_tester.py --sample saq
```

### **Web Frontend**
```bash
# Setup & Development
cd webfrontend
npm install
npm run dev
# Available at: http://127.0.0.1:8000

# Feature Branch Workflow (REQUIRED for GitHub issues)
git checkout -b feature/web-issue-37-cross-browser-testing
# Work on issue, then:
git add . && git commit -m "[WEB] Issue #37: Description"
git push -u origin feature/web-issue-37-cross-browser-testing
gh pr create --title "[WEB] Issue #37: Title" --body "Description"
gh pr merge --squash --delete-branch
git checkout main && git pull origin main
```

### **iOS App**
- **Build**: ⌘+B in Xcode
- **Run**: ⌘+R in Xcode  
- **Backend Required**: Ensure Python backend running on localhost:8000

## Essay Types Supported
- **DBQ** (Document-Based Question) - 6 points
- **LEQ** (Long Essay Question) - 6 points  
- **SAQ** (Short Answer Question) - 3 points with type differentiation:
  - **Stimulus SAQ** - Uses primary/secondary source document
  - **Non-Stimulus SAQ** - Pure text-based questions  
  - **Secondary Comparison SAQ** - Compares historical interpretations

## AI Configuration

### **Environment Setup**
Create `.env` file in `/backend/` directory:
```bash
# Development (default)
AI_SERVICE_TYPE=mock

# Production (requires API key)
AI_SERVICE_TYPE=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

### **AI Service Features**
- **Mock AI**: Realistic responses for testing, no API key required
- **Anthropic AI**: Claude 3.5 Sonnet, ~$0.02-0.03 per essay
- **Rate Limiting**: 20 req/min, 50 essays/hour, 50 essays/day
- **Cost Protection**: Built-in usage limits and tracking

## Testing Status
- **Backend**: 51 tests passing, production-ready ✅
- **iOS**: Complete API integration ✅
- **Web**: Progressive testing through GitHub issues #23-38

## Architecture Benefits
- **Simplified for 2-12 teachers**: 87% complexity reduction from original enterprise design
- **Multi-Platform**: Single backend serves both iOS and web frontends
- **Cost Protected**: Appropriate daily limits prevent excessive API costs
- **Easy Maintenance**: Clean, direct Python codebase structure

## Code Documentation Guidelines

### **Comment Philosophy**
Documentation should capture **design decisions and intentions** at the time of creation, not just functionality. Comments should explain the "why" and "when," not just the "what."

### **Good vs Poor Comments**

**❌ Poor (describes functionality):**
```python
# This function splits the input data into two equally sized chunks, 
# multiplies each chunk with Y and then adds it together
def process_chunks(data, multiplier):
```

**✅ Good (explains design decision):**
```python
# The hardware X that this code runs on has a cache size of Y which 
# makes this split necessary for optimal compute throughput
def process_chunks(data, multiplier):
```

### **Three Types of Documentation (Airplane Metaphor)**
1. **800-page manual** - Comprehensive but overwhelming ("Congratulations on purchasing your 747!")
2. **10-page guide** - Practical how-to ("How to change the oil in the engine")  
3. **5-item checklist** - Critical emergency procedures ("How to deal with a fire in the engine")

**Use type 2 and 3 for code comments** - focus on practical understanding and critical design decisions.

### **What to Document**
- **Hardware constraints** that influenced implementation choices
- **Performance considerations** that drove specific algorithms
- **Historical context** for unusual patterns ("This works around API limitation X")
- **Future considerations** ("When new hardware Y is available, consider Z approach")
- **Critical failure modes** and why specific safeguards exist

### **What NOT to Document**
- Obvious functionality that code already expresses
- Implementation details that are self-evident
- Redundant descriptions of what the code does

Remember: Future engineers need to understand **why** code exists in its current form to make informed decisions about changes.

## Development Workflow

### **Web Frontend GitHub Issues**
Follow sequential GitHub issues #23-38 for ChatGPT-style web interface:
- **ALWAYS use feature branches** for each issue (see commands above)
- Update WEB_FRONTEND_PLAN.md after completing each issue
- Create PRs referencing issue numbers
- Current: Issue #38 (Backend Integration & Production Deployment)

### **Git Authentication**
If authentication issues occur:
```bash
echo "your-github-token" | gh auth login --with-token
gh repo set-default kpfister44/APUSH-Grader
```

### **IDE Configuration (PyCharm)**
For proper environment variable loading in PyCharm CE:
1. **Run → Edit Configurations**
2. Set **Working directory** to: `/Users/kyle.pfister/APUSH-Grader/backend`
3. This ensures PyCharm finds the `.env` file and loads `AI_SERVICE_TYPE=anthropic`
4. Without correct working directory, system defaults to mock AI service

**Note**: Terminal execution automatically uses correct working directory, but IDEs may need manual configuration.

## Important Notes
- **Feature Branch Workflow**: REQUIRED for all web frontend development
- **Issue-Based Development**: Follow GitHub issues #23-38 sequentially
- **Backend Complete**: Production-ready with simplified architecture
- **API Documentation**: Available at http://localhost:8000/docs
- **See WEB_FRONTEND_PLAN.md**: Complete web frontend development plan and specifications