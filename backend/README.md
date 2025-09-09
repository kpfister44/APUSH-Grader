# APUSH Grader Backend

Python FastAPI backend for the APUSH Grader application. This backend provides AI-powered grading for AP US History essays using Anthropic Claude 3.5 Sonnet with simplified architecture designed for 2-12 teachers.

## Features

- **Complete Essay Grading**: Supports DBQ, LEQ, and SAQ essays with College Board rubrics
- **Dual SAQ Rubric Support**: College Board (3-point) and EG (10-point A/C/E criteria) rubrics
- **SAQ Type Differentiation**: Specialized grading for stimulus, non-stimulus, and secondary comparison SAQs
- **Teacher Authentication**: Password-protected access for authorized educators
- **Real AI Integration**: Anthropic Claude 3.5 Sonnet with configurable mock AI for development
- **Production Ready**: Rate limiting, usage tracking, health monitoring, CORS configuration
- **Manual Testing Tools**: Comprehensive script for testing real essays
- **Multi-Platform Integration**: Complete API for iOS and web frontends with structured responses

## Essay Types Supported

- **DBQ** (Document-Based Question) - 6 points
- **LEQ** (Long Essay Question) - 6 points  
- **SAQ** (Short Answer Question) - **Dual rubric support**:
  - **College Board Rubric** (3 points): Traditional part_a/b/c scoring
  - **EG Rubric** (10 points): A/C/E criteria with content-focused approach
  - **SAQ Types**: Stimulus, Non-Stimulus, Secondary Comparison

## Project Structure

```
backend/
├── app/
│   ├── main.py                     # FastAPI application entry point
│   ├── config/
│   │   └── settings.py             # Configuration management
│   ├── models/
│   │   ├── core.py                 # Core models (EssayType, SAQType, GradeResponse)
│   │   ├── processing.py           # Processing models 
│   │   └── requests/               # API request/response models
│   ├── api/
│   │   └── routes/
│   │       ├── grading.py          # POST /api/v1/grade endpoint (protected)
│   │       ├── auth.py             # Authentication endpoints
│   │       └── health.py           # Health check endpoints
│   ├── services/
│   │   └── ai/                     # AI service integration
│   ├── utils/                      # Utility functions
│   │   ├── grading_workflow.py     # Complete grading workflow
│   │   ├── prompt_generation.py    # AI prompt generation
│   │   ├── essay_processing.py     # Essay validation and processing
│   │   └── response_processing.py  # AI response processing
│   └── middleware/
│       └── rate_limiting.py        # Rate limiting middleware
├── tests/                          # Test suite (51 tests)
├── sample_essays/                  # Sample essays for manual testing
│   ├── dbq_essay.txt
│   ├── leq_essay.txt
│   ├── saq_*_essay.txt            # SAQ type-specific samples
│   └── prompts/                   # Corresponding prompts
├── manual_essay_tester.py          # Manual testing script
├── requirements.txt                # Core dependencies
├── requirements-dev.txt            # Development dependencies
└── README.md                       # This file
```

## Quick Start

### Prerequisites

- Python 3.12 (recommended for M-series Mac compatibility)
- pip

### Installation

1. **Create virtual environment**:
   ```bash
   cd backend
   python3.12 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Set up environment variables**:
   ```bash
   # For real AI grading (optional - defaults to mock AI)
   export ANTHROPIC_API_KEY='sk-ant-api03-your-key-here'
   export AI_SERVICE_TYPE='anthropic'
   
   # For authentication (required in production)
   export AUTH_PASSWORD='your-secure-password'
   ```

### Running the Application

```bash
# Start development server
source venv/bin/activate
uvicorn app.main:app --reload

# Application available at:
# - API: http://localhost:8000
# - Interactive docs: http://localhost:8000/docs
# - Health check: http://localhost:8000/health
# - Usage summary: http://localhost:8000/usage/summary
```

## Manual Essay Testing

Test the grading system with real essays using the manual testing script:

```bash
# Test with sample essays
python manual_essay_tester.py --sample dbq
python manual_essay_tester.py --sample leq
python manual_essay_tester.py --sample saq

# Test SAQ type differentiation
python manual_essay_tester.py --sample saq stimulus
python manual_essay_tester.py --sample saq non_stimulus
python manual_essay_tester.py --sample saq secondary_comparison

# Test with your own essays
python manual_essay_tester.py my_essay.txt dbq my_prompt.txt

# Interactive mode
python manual_essay_tester.py
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run integration tests
pytest tests/integration/ -v

# Run specific test categories
pytest tests/test_grading_workflow.py -v
pytest tests/test_utils.py -v
```

## API Endpoints

### Authentication
- **POST** `/auth/login` - Teacher login (rate limited: 10/min)
- **POST** `/auth/logout` - Logout and invalidate session
- **GET** `/auth/verify` - Verify session token validity

### Grading (Protected - Requires Authentication)
- **POST** `/api/v1/grade` - Grade an essay (rate limited: 20/min, 50/hour)
- **GET** `/api/v1/grade/status` - Grading service status

### Health & Monitoring
- **GET** `/health` - Application health status
- **GET** `/usage/summary` - Daily usage summary
- **GET** `/` - Root endpoint

### Example Authentication Request

```json
{
  "password": "your-teacher-password"
}
```

### Example Grading Request

```json
{
  "essay_type": "SAQ",
  "saq_type": "stimulus", 
  "rubric_type": "college_board",
  "prompt": "Use the excerpt below to answer all parts...",
  "saq_parts": {
    "part_a": "Student response to part A",
    "part_b": "Student response to part B", 
    "part_c": "Student response to part C"
  }
}
```

### Example Response

```json
{
  "score": 2,
  "max_score": 3,
  "percentage": 66.7,
  "letter_grade": "C",
  "performance_level": "Proficient",
  "breakdown": {
    "part_a": {"score": 1, "max_score": 1, "feedback": "..."},
    "part_b": {"score": 1, "max_score": 1, "feedback": "..."},
    "part_c": {"score": 0, "max_score": 1, "feedback": "..."}
  },
  "overall_feedback": "Good responses to parts A and B...",
  "suggestions": ["Provide more specific details...", "..."],
  "word_count": 165,
  "paragraph_count": 3
}
```

## Configuration

### AI Service Configuration

The system supports two AI modes:

**Mock AI (Default)**:
```bash
# No API key required - uses realistic mock responses
AI_SERVICE_TYPE=mock
```

**Real Anthropic AI**:
```bash
# Requires API key - uses Claude 3.5 Sonnet
AI_SERVICE_TYPE=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

### Environment Variables

- `AI_SERVICE_TYPE` - AI service type (`mock` or `anthropic`)
- `ANTHROPIC_API_KEY` - Anthropic API key (required for real AI)
- `AUTH_PASSWORD` - Teacher authentication password (required for production)
- `DEBUG` - Enable debug mode (default: `false`)
- `ALLOWED_ORIGINS` - CORS allowed origins
- `CORS_CREDENTIALS` - CORS credentials (default: `true`)

## Rate Limiting & Usage

- **Rate Limits**: 20 requests/minute, 50 essays/hour
- **Daily Limits**: 50 essays/day, 10,000 words/essay
- **Cost Protection**: Built-in safeguards for Anthropic API usage
- **Usage Tracking**: Simple daily counter via `/usage/summary`

## Architecture

**Simplified for Hobby Project Scale (2-12 Teachers)**:
- Direct utility functions (no complex dependency injection)
- Basic logging and usage tracking
- Essential test coverage (51 focused tests)
- Consolidated models (3 files vs original 12)
- 87% complexity reduction from enterprise patterns

## Production Deployment

**✅ LIVE IN PRODUCTION**

### Production URLs
- **🌐 Web App**: https://apushgrader.vercel.app (requires teacher authentication)
- **🔧 Backend API**: https://apush-grader-production.up.railway.app
- **📚 API Docs**: https://apush-grader-production.up.railway.app/docs

### Screenshots
<!-- TODO: Add web app screenshots here -->
<!-- Example:
![APUSH Grader Login Screen](screenshots/login-screen.png)
![APUSH Grader Interface](screenshots/grading-interface.png)
-->

### Deployment Status
- ✅ **Backend**: Railway production deployment with authentication
- ✅ **Frontend**: Vercel deployment with login screen
- ✅ **Authentication**: Password-protected teacher access
- ✅ **Multi-Platform**: iOS app and web frontend integration

## Development Status

**✅ PRODUCTION READY** - Complete Implementation

- ✅ Complete FastAPI backend with simplified architecture
- ✅ Teacher authentication system with session management
- ✅ Dual SAQ rubric support (College Board + EG rubrics)
- ✅ SAQ type differentiation for improved grading accuracy
- ✅ Real Anthropic Claude 3.5 Sonnet integration
- ✅ Rate limiting, usage tracking, health monitoring
- ✅ Manual essay testing system
- ✅ Multi-platform integration (iOS + Web)
- ✅ Comprehensive test suite (51 tests)
- ✅ Cost protection and usage safeguards

## Cost Information

- **Anthropic Claude 3.5 Sonnet**: ~$0.02-0.03 per essay
- **Daily limits prevent excessive costs**: 50 essays/day maximum
- **Rate limiting**: Prevents abuse and manages costs
- **Mock AI available**: No cost for development and testing