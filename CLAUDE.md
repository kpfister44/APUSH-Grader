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