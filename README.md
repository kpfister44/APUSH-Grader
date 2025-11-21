# APUSH Grader

An AI-powered essay grading system for AP US History teachers, providing instant, detailed feedback on DBQ, LEQ, and SAQ essays using Anthropic Claude Sonnet 4.5 with official College Board rubrics.

**Live Application:** https://apushgrader.vercel.app

![APUSH Grader - Main Interface](./docs/screenshots/main-interface.png)
*Screenshot: Claude style interface for essay input and grading*

---

## Overview

Grading AP US History essays shouldn't take days to provide feedback. Teachers need to return graded essays quickly so students can learn and improve before the next assignment. This application transforms the essay grading workflow from hours of manual evaluation to instant, comprehensive AI-powered feedback.

**What it does:**
- **Grades** DBQ (6 pts), LEQ (6 pts), and SAQ (3 pts or 10 pts) essays using official rubrics
- **Analyzes** essays against College Board scoring criteria with detailed breakdowns
- **Provides** comprehensive feedback with strengths, improvements, and strategic tips
- **Supports** dual SAQ rubrics: College Board (3-point) and custom EG (10-point A/C/E)
- **Enables** DBQ document upload with vision AI for chart/graph analysis
- **Generates** PDF reports for record-keeping and parent conferences

**Why I built this:**

As a high school AP US History teacher, I needed a way to provide timely, consistent feedback on student essays without spending 3-4 hours per class set. This project demonstrates practical application of AI for education while showcasing modern full-stack development: FastAPI backend architecture, React/TypeScript frontend, AI integration patterns, and production deployment strategies.

**Key Achievement:** Reduced essay grading time from 3-4 hours per class to instant feedback while maintaining College Board rubric accuracy and providing more detailed, actionable suggestions than manual grading alone.

---

## Live Demo

**Frontend:** https://apushgrader.vercel.app
**Backend API:** https://apush-grader-production.up.railway.app
**API Documentation:** https://apush-grader-production.up.railway.app/docs (Interactive Swagger UI)

**Login:** Password-protected for teachers (contact for access)

---

## Features & Technical Highlights

### 1. Multi-Essay Type Support

Grade all AP US History essay formats with appropriate rubrics:

**Document-Based Question (DBQ) - 6 points:**
- Thesis/Claim (1 pt)
- Contextualization (1 pt)
- Evidence from Documents (2 pts)
- Evidence Beyond Documents (1 pt)
- Analysis and Reasoning (1 pt)

**Long Essay Question (LEQ) - 6 points:**
- Thesis (1 pt)
- Contextualization (1 pt)
- Evidence (2 pts)
- Analysis and Reasoning (2 pts)

**Short Answer Question (SAQ) - 3 or 10 points:**
- **College Board rubric:** Part A/B/C (1 pt each)
- **EG custom rubric:** Criterion A (content), C (citation), E (extension)

**Technical highlights:**
- Dynamic rubric selection based on essay type
- Rubric-specific prompt engineering for accurate evaluation
- Structured JSON response parsing with type-safe Pydantic models
- Dual rubric system for classroom flexibility

---

### 2. Claude Style Web Interface

Modern, intuitive interface designed for teacher workflow:

![Grading Interface](./docs/screenshots/saq-interface.png)
*Screenshot: Essay type selection and input interface for SAQ*

![Grading Interface](./docs/screenshots/leq-interface.png)
*Screenshot: Essay type selection and input interface for LEQ*

**User Experience:**
- Clean, distraction-free design
- Real-time validation feedback
- Loading states with progress indicators
- Mobile-responsive layout (works on tablets/phones)
- One-click PDF export for record-keeping

**Technical highlights:**
- React 19 with functional components and hooks
- TypeScript for type safety across frontend
- Context API for clean state management (no Redux complexity)
- Tailwind CSS v4 for utility-first styling
- ESBuild for fast development and builds (~50ms rebuilds)

---

### 3. DBQ Vision API Integration

Upload DBQ document images for AI-powered visual analysis:

![DBQ Document Upload](./docs/screenshots/dbq-interface.png)
*Screenshot: DBQ document upload interface (7 images)*

**Capabilities:**
- **Chart analysis:** Reads and interprets historical data visualizations
- **Graph interpretation:** Analyzes trends and patterns in visual data
- **Political cartoons:** Understands symbolism and historical context
- **Text extraction:** Reads printed and handwritten text from images

**Cost Optimization:**
- Session-based document caching (2-hour expiration)
- Anthropic Prompt Caching for 90% cost reduction on batch grading
- Single upload → grade multiple student essays using same documents

**Technical highlights:**
- Anthropic Vision API integration
- Base64 image encoding and transmission
- Multipart form data handling
- In-memory session cache for performance
- Graceful fallback to text-only mode

---

### 4. Intelligent AI Grading Engine

Powered by Anthropic Claude Sonnet 4.5 for superior historical analysis:

![Grading Results](./docs/screenshots/main-grading-interface.png)
*Screenshot: The main grading interface*

![Grading Results](./docs/screenshots/detailed-score-breakdown.png)
*Screenshot: Detailed grading results with rubric breakdown*

**AI Features:**
- Structured prompt engineering with explicit rubric criteria
- JSON-validated responses for consistent parsing
- Nuanced historical knowledge and analysis
- Contextual understanding of AP US History content
- Low temperature (0.3) for grading consistency

**Feedback Quality:**
- Score breakdown by rubric criteria
- Specific strengths with examples from essay
- Targeted improvements with actionable suggestions
- Performance level indicators (Advanced/Proficient/Basic)
- Word count and paragraph analysis

**Technical highlights:**
- `claude-sonnet-4-5-20250929` model (latest Sonnet 4.5)
- Async/await for non-blocking API calls
- Retry logic with exponential backoff
- Comprehensive error handling and logging
- Mock AI service for development/testing

---

### 5. Production-Ready Features

Built for reliable classroom use with cost protection:

**Rate Limiting:**
- 20 requests/minute
- 50 essays/hour
- 100 essays/day

**Usage Safeguards:**
- 10,000 words max per essay
- 50,000 words/day limit
- Cost tracking and monitoring
- Real-time usage dashboard

**Monitoring & Logging:**
- JSON structured logging with correlation IDs
- Health check endpoints (`/health`, `/health/detailed`)
- Usage summary endpoint (`/usage/summary`)
- Error tracking and alerting

**Technical highlights:**
- SlowAPI rate limiting middleware
- Pydantic request/response validation
- FastAPI dependency injection for auth
- CORS configuration for secure cross-origin requests
- Environment-based configuration management

---

### 6. Teacher Authentication System

Basic password-protected access with session management:

![Login Screen](./docs/screenshots/login-screen.png)
*Screenshot: Teacher login interface*

**Security:**
- Session token authentication
- 24-hour token expiration
- Secure password validation
- Protected API endpoints
- Rate-limited login attempts (10/min)

**User Experience:**
- Persistent login via localStorage
- Auto-logout on token expiry
- Friendly error messages
- One-time password setup

**Technical highlights:**
- Session-based auth (no database required at 2-12 teacher scale)
- React Context for auth state management
- Authorization header injection on API calls
- Protected route components with redirect

---

## Tech Stack

### Backend
- **Python 3.12** - Modern async Python with type hints
- **FastAPI 0.104** - High-performance async web framework with automatic OpenAPI docs
- **Anthropic SDK 0.57** - Official Claude API client with vision support
- **Pydantic 2.5** - Data validation and serialization
- **pytest** - Comprehensive testing framework (51 focused tests)

### Frontend
- **React 19.1.0** - Modern UI library with concurrent features
- **TypeScript 5.8.3** - Type-safe JavaScript for better DX
- **Tailwind CSS 4.1.11** - Utility-first CSS framework
- **React Router 7.7.0** - Client-side routing for SPA
- **ESBuild 0.25.8** - Lightning-fast bundler and dev server
- **@react-pdf/renderer 4.3.0** - Client-side PDF generation

### AI Integration
- **Anthropic Claude Sonnet 4.5** - Most intelligent model for complex reasoning
- **Vision API** - Native image understanding for DBQ documents
- **Structured outputs** - JSON-validated responses for reliable parsing

### Deployment & Infrastructure
- **Railway** - Backend hosting with automatic deploys from GitHub
- **Vercel** - Frontend hosting with edge network distribution
- **Auto-deployment** - Pushes to `main` branch trigger production updates
- **Environment isolation** - Separate dev/prod configurations

---

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Browser                             │
│   ┌─────────────────────────────────────────────────┐       │
│   │  React Frontend (Vercel)                        │       │
│   │  - ChatGPT-style UI                             │       │
│   │  - Essay input forms                            │       │
│   │  - Results display                              │       │
│   │  - PDF export                                   │       │
│   └──────────────────┬──────────────────────────────┘       │
└────────────────────────│────────────────────────────────────┘
                         │
                         │ HTTPS/JSON
                         │ (authenticated)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│             FastAPI Backend (Railway)                       │
│                                                             │
│   ┌────────────────┐  ┌─────────────────┐  ┌────────────┐ │
│   │ Auth           │  │ Grading         │  │ DBQ Docs   │ │
│   │ Middleware     │  │ Workflow        │  │ Upload     │ │
│   └────────────────┘  └─────────────────┘  └────────────┘ │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐  │
│   │ Services Layer                                      │  │
│   │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │  │
│   │  │ Prompt       │  │ Response     │  │ Session   │ │  │
│   │  │ Generation   │  │ Processing   │  │ Cache     │ │  │
│   │  └──────────────┘  └──────────────┘  └───────────┘ │  │
│   └─────────────────────────────────────────────────────┘  │
│                             │                               │
└─────────────────────────────┼───────────────────────────────┘
                              │
                              │ HTTPS/JSON
                              ▼
┌─────────────────────────────────────────────────────────────┐
│           Anthropic Claude API                              │
│                                                             │
│   ┌──────────────────┐         ┌──────────────────┐        │
│   │ Text Analysis    │         │ Vision API       │        │
│   │ (Essay grading)  │         │ (DBQ documents)  │        │
│   └──────────────────┘         └──────────────────┘        │
│                                                             │
│   Model: claude-sonnet-4-5-20250929                        │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow

**Essay Grading Workflow:**

1. **User Input** - Teacher enters essay text, prompt, and selects essay type
2. **Frontend Validation** - TypeScript type checking and form validation
3. **API Request** - Authenticated POST to `/api/v1/grade` with JSON payload
4. **Backend Processing:**
   - Validate request with Pydantic models
   - Generate AI prompt based on essay type and rubric
   - Call Anthropic API with structured prompt
   - Parse JSON response into typed GradeResponse
   - Calculate performance metrics
5. **Response** - Return structured grading results to frontend
6. **Display** - Render results with score visualization and PDF export option

**DBQ Document Upload Flow:**

1. **Image Upload** - Teacher uploads 7 JPEG images (max 5MB each)
2. **Backend Storage** - Store in session cache with 2-hour expiration
3. **Return ID** - Send `document_set_id` to frontend
4. **Grading Request** - Include `document_set_id` in subsequent grade requests
5. **Vision API** - Send images + essay text to Claude Vision API
6. **Cache Hit** - Reuse documents for batch grading (multiple students)

---

## Project Structure

```
APUSH-Grader/
├── backend/                           # Python FastAPI Backend
│   ├── app/
│   │   ├── api/routes/                # REST API endpoints
│   │   │   ├── grading.py             # POST /api/v1/grade (main grading endpoint)
│   │   │   ├── dbq.py                 # DBQ document upload endpoints
│   │   │   ├── auth.py                # Authentication endpoints
│   │   │   └── health.py              # Health check and usage monitoring
│   │   ├── models/                    # Pydantic data models
│   │   │   ├── core.py                # EssayType, RubricType, SAQType enums
│   │   │   ├── processing.py          # Internal processing models
│   │   │   └── requests/              # API request/response models
│   │   ├── services/ai/               # AI integration layer
│   │   │   ├── anthropic_service.py   # Claude API client (text + vision)
│   │   │   ├── mock_service.py        # Development mock AI
│   │   │   ├── base.py                # AI service interface
│   │   │   └── factory.py             # Service locator pattern
│   │   ├── utils/                     # Business logic utilities
│   │   │   ├── grading_workflow.py    # Main orchestration logic
│   │   │   ├── prompt_generation.py   # AI prompt builders (dual rubric)
│   │   │   ├── response_processing.py # Parse AI JSON responses
│   │   │   ├── essay_processing.py    # Text validation and analysis
│   │   │   └── simple_usage.py        # Usage tracking (daily counters)
│   │   ├── middleware/                # Production middleware
│   │   │   ├── rate_limiting.py       # SlowAPI rate limits
│   │   │   └── auth.py                # Session token validation
│   │   ├── config/
│   │   │   └── settings.py            # Environment configuration
│   │   ├── exceptions.py              # Custom exception classes
│   │   └── main.py                    # FastAPI app initialization
│   ├── tests/                         # 51 comprehensive tests
│   │   ├── integration/               # End-to-end workflow tests
│   │   └── services/                  # Unit tests for services
│   ├── sample_essays/                 # Manual testing samples
│   ├── manual_essay_tester.py         # CLI testing tool
│   ├── requirements.txt               # Production dependencies
│   ├── requirements-dev.txt           # Development dependencies
│   ├── .env.example                   # Environment template
│   ├── Procfile                       # Railway deployment config
│   └── BACKEND.md                     # Detailed backend documentation
│
├── webfrontend/                       # React/TypeScript Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   │   └── LoginScreen.tsx    # Password authentication UI
│   │   │   ├── input/                 # Essay input components
│   │   │   │   ├── EssayTypeSelector.tsx
│   │   │   │   ├── SAQTypeSelector.tsx
│   │   │   │   ├── RubricTypeSelector.tsx
│   │   │   │   ├── PromptInput.tsx
│   │   │   │   ├── SAQMultiPartInput.tsx
│   │   │   │   ├── ChatTextArea.tsx
│   │   │   │   └── DocumentUpload.tsx
│   │   │   ├── ui/                    # Display components
│   │   │   │   ├── ResultsDisplay.tsx
│   │   │   │   ├── ScoreVisualizer.tsx
│   │   │   │   ├── SubmitButton.tsx
│   │   │   │   └── ValidationFeedback.tsx
│   │   │   ├── pdf/                   # PDF generation
│   │   │   │   ├── PDFExport.tsx
│   │   │   │   ├── PDFEssayPage.tsx
│   │   │   │   └── PDFResultsPage.tsx
│   │   │   └── layout/                # Layout components
│   │   ├── contexts/                  # React Context state management
│   │   │   ├── AuthContext.tsx        # Authentication state
│   │   │   └── GradingContext.tsx     # Essay grading workflow state
│   │   ├── services/
│   │   │   └── api.ts                 # Backend API client (fetch-based)
│   │   ├── types/                     # TypeScript definitions
│   │   │   ├── api.ts                 # Backend API types (matches Pydantic)
│   │   │   └── ui.ts                  # UI-specific types
│   │   ├── pages/
│   │   │   ├── GradingPage.tsx        # Main grading interface
│   │   │   └── LoginPage.tsx          # Login screen
│   │   ├── styles/
│   │   │   └── index.css              # Tailwind imports + custom CSS
│   │   ├── App.tsx                    # Root component with routing
│   │   └── index.tsx                  # React app entry point
│   ├── public/                        # Static assets
│   ├── dist/                          # Production build output
│   ├── build.js                       # ESBuild configuration
│   ├── package.json                   # Frontend dependencies
│   ├── tsconfig.json                  # TypeScript configuration
│   ├── vercel.json                    # Vercel deployment config
│   └── FRONTEND.md                    # Detailed frontend documentation
│
├── docs/
│   └── screenshots/                   # Application screenshots
│       ├── main-interface.png
│       ├── grading-interface.png
│       ├── dbq-upload.png
│       ├── results-display.png
│       └── login-screen.png
│
├── CLAUDE.md                          # AI development guidance
└── README.md                          # This file
```

---

## Quick Start

### Prerequisites

- **Backend:** Python 3.12+, Anthropic API key
- **Frontend:** Node.js 18+, npm
- **Target Audience:** 2-12 AP US History teachers (hobby project scale)

### 1. Setup Backend

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configure environment
cp .env.example .env
# Edit .env and add your Anthropic API key:
# AI_SERVICE_TYPE=anthropic
# ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
# AUTH_PASSWORD=your-teacher-password

# Run the server
uvicorn app.main:app --reload
```

**Backend running at:** http://localhost:8000
**API Documentation:** http://localhost:8000/docs

### 2. Setup Frontend

```bash
# Navigate to frontend directory (from project root)
cd webfrontend

# Install dependencies
npm install

# Run development server
npm run dev
```

**Frontend running at:** http://127.0.0.1:8001

### 3. Test Integration

1. **Start backend** (see step 1)
2. **Start frontend** (see step 2)
3. **Open browser** to http://127.0.0.1:8001
4. **Login** with teacher password
5. **Select essay type** (DBQ, LEQ, or SAQ)
6. **Enter prompt** and essay text
7. **Click "Grade Essay"** to test end-to-end integration
8. **View results** with AI-powered feedback

---

## Configuration

### Backend Environment Variables

Configure in `backend/.env` file:

```bash
# AI Service Configuration
AI_SERVICE_TYPE=mock              # "mock" for dev, "anthropic" for production
ANTHROPIC_API_KEY=sk-ant-...      # Required for production

# Authentication
AUTH_PASSWORD=eghsAPUSH           # Teacher password for login

# CORS Origins (comma-separated)
ALLOWED_ORIGINS=http://localhost:8001,https://apushgrader.vercel.app

# Debug Mode
DEBUG=false                        # Set to true for verbose logging
```

### Frontend Configuration

Production API URL is hardcoded in `src/services/api.ts` due to ESBuild environment variable limitations:

```typescript
const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? 'https://apush-grader-production.up.railway.app'
  : 'http://localhost:8000';
```

For development, backend is automatically detected at `http://localhost:8000`.

---

## Performance

### Timing Breakdown

**Single Essay Grading:**

| Step | Time | Notes |
|------|------|-------|
| Frontend validation | <0.1s | Client-side type checking |
| API request (network) | ~0.2s | Local or Railway hosting |
| Prompt generation | <0.1s | Template-based, in-memory |
| **Anthropic API call** | **2-5s** | **BOTTLENECK** |
| Response parsing | <0.1s | JSON deserialization |
| Frontend rendering | <0.1s | React DOM updates |

**Total:** ~2-6 seconds per essay

**Batch Grading (40 students):**

| Scenario | Time | Notes |
|----------|------|-------|
| Sequential grading | 80-240s | ~2-6s per essay × 40 |
| With DBQ caching | 80-240s | First run (documents uploaded) |
| Re-run with cache | Same | No caching benefit for unique essays |

### Cost Analysis

**Anthropic Claude Sonnet 4.5 Pricing:**

| Item | Cost | Notes |
|------|------|-------|
| Input tokens (prompt) | ~$3.00 per 1M tokens | Rubric + essay text |
| Output tokens (feedback) | ~$15.00 per 1M tokens | Grading response |
| **Typical essay** | **~$0.02-0.03** | **Standard DBQ/LEQ** |
| DBQ with images | ~$0.02-0.04 | Vision API included |
| 40-essay class | ~$0.80-1.20 | One grading session |

**Cost Protection:**
- Daily limits: 100 essays/day, 50,000 words/day
- Rate limiting: 20 requests/minute, 50 essays/hour
- Usage tracking via `/usage/summary` endpoint

---

## Testing

### Backend Tests (pytest)

```bash
cd backend
source venv/bin/activate

# Run all 51 tests
pytest tests/ -v

# Run specific test categories
pytest tests/integration/ -v           # End-to-end workflows
pytest tests/services/ -v              # AI service integration

# Run with coverage
pytest tests/ --cov=app --cov-report=term-missing

# Manual testing with sample essays
python manual_essay_tester.py --sample dbq
python manual_essay_tester.py --sample saq stimulus
```

**Test Coverage:**
- 51 focused tests covering essential paths
- Integration tests for complete grading workflows
- Unit tests for prompt generation, response parsing, and validation
- Mock AI service for fast, deterministic testing

### Frontend Testing

**Development Testing:**
- Type checking: `npx tsc --noEmit`
- Component testing: Manual testing in browser
- Integration testing: End-to-end with backend API
- Responsive testing: Browser DevTools device emulation

---

## API Endpoints

**Production:** https://apush-grader-production.up.railway.app
**Interactive Docs:** https://apush-grader-production.up.railway.app/docs

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/login` | POST | Teacher authentication (returns session token) |
| `/auth/logout` | POST | End session and invalidate token |
| `/auth/verify` | GET | Check if token is valid |
| `/api/v1/grade` | POST | Grade essay (protected - requires auth) |
| `/api/v1/dbq/documents` | POST | Upload DBQ document images (protected) |
| `/api/v1/dbq/documents/{id}` | GET | Get document set metadata |
| `/health` | GET | Basic health check |
| `/health/detailed` | GET | Detailed system health |
| `/usage/summary` | GET | Daily usage statistics |

### Example API Calls

**Login:**
```bash
curl -X POST https://apush-grader-production.up.railway.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{"password":"eghsAPUSH"}'
```

**Grade Essay:**
```bash
curl -X POST https://apush-grader-production.up.railway.app/api/v1/grade \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "essay_type": "SAQ",
    "saq_type": "stimulus",
    "rubric_type": "college_board",
    "prompt": "Question text here...",
    "saq_parts": {
      "part_a": "Student answer to part A",
      "part_b": "Student answer to part B",
      "part_c": "Student answer to part C"
    }
  }'
```

---

## Production Deployment

### Backend (Railway)

**URL:** https://apush-grader-production.up.railway.app

**Configuration:**
- **Platform:** Railway.app
- **Runtime:** Python 3.12
- **Web Server:** Uvicorn ASGI server
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Auto-deploy:** Pushes to `main` branch trigger deployment
- **Environment Variables:** Set in Railway dashboard

**Health Monitoring:**
- `/health` endpoint for uptime checks
- `/usage/summary` for usage tracking
- Structured JSON logging for debugging

### Frontend (Vercel)

**URL:** https://apushgrader.vercel.app

**Configuration:**
- **Platform:** Vercel
- **Framework:** React (custom build with ESBuild)
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Auto-deploy:** Pushes to `main` branch trigger deployment
- **Edge Network:** Global CDN for fast loading

**vercel.json:**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": null
}
```

### Deployment Workflow

1. **Develop locally** with hot-reload dev servers
2. **Test** against local backend and API docs
3. **Commit and push** to `main` branch on GitHub
4. **Automatic deployment:**
   - Railway rebuilds backend (2-3 minutes)
   - Vercel rebuilds frontend (1-2 minutes)
5. **Verify** at production URLs

---

## Documentation

Comprehensive technical documentation is available in the project:

- **[Backend Architecture](backend/BACKEND.md)** - FastAPI design, AI integration, testing strategy
- **[Frontend Architecture](webfrontend/FRONTEND.md)** - React components, state management, styling patterns

---

## Future Enhancements

### Planned Features
- [x] DBQ vision API for document image analysis (Phase 1 complete)
- [ ] Anthropic Prompt Caching for 90% cost reduction on batch grading
- [ ] Custom LEQ rubrics with teacher-defined criteria

### Technical Improvements
- [ ] Redis caching for session tokens at scale
- [ ] PostgreSQL database for persistent grading history
- [ ] Batch grading API for processing multiple essays in one request
- [ ] Real-time grading progress updates via WebSockets
- [ ] CI/CD pipeline with automated testing

---

## License

This project is for educational purposes and is not designed for scale or general distribution.

---

## Contact

**Kyle Pfister**

- **GitHub:** [@kpfister44](https://github.com/kpfister44)
- **LinkedIn:** https://www.linkedin.com/in/kyle-pfister-510753286/
- **Email:** kpfister44@gmail.com

**Have questions or want to discuss AI in education?** Feel free to reach out!

---

**Built with FastAPI, React, and Anthropic Claude Sonnet 4.5 to make AP US History essay grading instant and insightful.**
