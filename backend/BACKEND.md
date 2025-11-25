# Backend Architecture Documentation

**Python FastAPI Backend for APUSH Grader**

This document provides architectural context for Claude Code to understand the backend system quickly and begin development work.

## Core Philosophy

**Designed for 2-12 teachers** - Hobby project scale with intentional simplicity over enterprise patterns.

### Key Decisions
- **Direct utility functions** instead of complex dependency injection
- **Consolidated models** (3 files vs 12+ in enterprise patterns)
- **Essential test coverage** (51 focused tests, not 200+)
- **Simple usage tracking** (daily counters, not analytics databases)
- **87% complexity reduction** from original enterprise design

**Why:** Teachers need a working tool, not a complex system to maintain.

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                     # FastAPI app entry, CORS, middleware setup
│   ├── config/
│   │   └── settings.py             # Environment config (Pydantic BaseSettings)
│   ├── models/
│   │   ├── core.py                 # EssayType, RubricType, SAQType, GradeResponse
│   │   ├── processing.py           # Internal processing models
│   │   └── requests/
│   │       ├── grading.py          # GradeRequest/Response for /api/v1/grade
│   │       └── auth.py             # LoginRequest/Response, session models
│   ├── api/routes/
│   │   ├── grading.py              # POST /api/v1/grade (protected)
│   │   ├── auth.py                 # POST /auth/login, /auth/logout, GET /auth/verify
│   │   └── health.py               # GET /health, /usage/summary
│   ├── services/
│   │   └── ai/
│   │       ├── service_locator.py  # AI service factory (mock vs real)
│   │       ├── anthropic_service.py # Real Claude Sonnet 4 integration
│   │       └── mock_service.py     # Development mock AI
│   ├── utils/
│   │   ├── grading_workflow.py     # Main orchestration: grade_essay()
│   │   ├── prompt_generation.py    # AI prompt builders (dual rubric support)
│   │   ├── essay_processing.py     # Text analysis, validation
│   │   └── response_processing.py  # Parse AI responses to structured data
│   └── middleware/
│       ├── rate_limiting.py        # SlowAPI rate limits
│       └── auth.py                 # Session token validation
├── tests/                          # 51 focused tests
├── sample_essays/                  # Manual testing samples
└── manual_essay_tester.py          # CLI testing tool
```

---

## Core Data Models

### Essay Types (`app/models/core.py`)

```python
class EssayType(str, Enum):
    DBQ = "DBQ"  # Document-Based Question (6 points)
    LEQ = "LEQ"  # Long Essay Question (6 points)
    SAQ = "SAQ"  # Short Answer Question (3 points)
```

### SAQ Type Differentiation

```python
class SAQType(str, Enum):
    STIMULUS = "stimulus"                   # Has source/stimulus
    NON_STIMULUS = "non_stimulus"           # No source provided
    SECONDARY_COMPARISON = "secondary_comparison"  # Compare 2+ sources
```

**Why SAQ types matter:** Different grading patterns for source analysis vs direct recall vs comparison.

### Dual Rubric Support (SAQ Only)

```python
class RubricType(str, Enum):
    COLLEGE_BOARD = "college_board"  # 3-point: part_a/b/c
    EG = "eg"                        # 10-point: A/C/E criteria
```

**College Board Rubric:**
- Traditional 3-point (part_a, part_b, part_c)
- Each part: 0 or 1 point
- Used in AP exam grading

**EG Rubric (Custom):**
- 10-point scale with A/C/E criteria
- Criterion A: Content accuracy (focus on factual correctness)
- Criterion C: Citation/evidence use
- Criterion E: Extension/analysis depth
- More granular feedback for classroom use

**Implementation:** Dual prompt generation in `prompt_generation.py` with separate response parsers in `response_processing.py`.

---

## API Architecture

### Authentication Flow

**Session-based authentication** for teacher access:

1. **POST /auth/login** (rate limited: 10/min)
   ```json
   { "password": "eghsAPUSH" }
   ```
   Returns: `{ "token": "...", "expires_at": "..." }`

2. **Session token stored** (in-memory dict, expires when backend restarts)
   - Simple for hobby project scale
   - Tokens expire after 24 hours
   - No persistent database needed

3. **Protected endpoints** use `verify_token()` dependency
   - All `/api/v1/*` endpoints require valid token
   - 401 if missing/invalid token

**Why simple sessions:** 2-12 teachers don't need Redis/JWT complexity.

### Grading Endpoint

**POST /api/v1/grade** - Main essay grading endpoint

**Request structure:**
```python
{
    "essay_type": "SAQ",
    "saq_type": "stimulus",      # Required if essay_type = SAQ
    "rubric_type": "college_board",  # Required if essay_type = SAQ
    "prompt": "Question text...",
    "saq_parts": {               # For SAQ only
        "part_a": "Student answer to part A",
        "part_b": "Student answer to part B",
        "part_c": "Student answer to part C"
    }
    # OR for DBQ/LEQ:
    "essay_text": "Full essay text..."
}
```

**Response structure:**
```python
{
    "score": 2,
    "max_score": 3,
    "percentage": 66.7,
    "letter_grade": "C",
    "performance_level": "Proficient",
    "breakdown": {
        # For College Board SAQ:
        "part_a": {"score": 1, "feedback": "..."},
        # OR for EG SAQ:
        "criterion_a": {"score": 7, "feedback": "..."},
        # OR for DBQ/LEQ:
        "thesis": {"score": 1, "feedback": "..."}
    },
    "overall_feedback": "Summary...",
    "suggestions": ["Tip 1", "Tip 2"],
    "word_count": 165,
    "paragraph_count": 3
}
```

**Rate limiting:**
- 20 requests/minute
- 50 essays/hour
- 50 essays/day
- 10,000 words max per essay

### DBQ Document Upload Endpoints

**POST /api/v1/dbq/documents** - Upload DBQ document images for vision-based grading

**Purpose:** Supports DBQ essays with image documents (charts, graphs, political cartoons, text images). Teachers upload 7 documents once, then grade multiple student essays using the same documents.

**Request:**
- Multipart form data with exactly 7 JPEG files
- Each file must be < 5MB
- Files labeled as Document 1-7 in upload order

**Response:**
```json
{
    "document_set_id": "uuid-string",
    "document_count": 7,
    "total_size_mb": 12.5,
    "expires_at": "2025-10-14T16:38:13"
}
```

**Storage:**
- In-memory session cache (like auth tokens)
- 2-hour expiration (perfect for batch grading)
- Documents cached for cost optimization

**Rate limiting:**
- 10 uploads per hour

**GET /api/v1/dbq/documents/{document_set_id}** - Get document set metadata

Returns document count, size, creation time, and expiration time.

**DELETE /api/v1/dbq/documents/{document_set_id}** - Delete document set

Manually removes documents before expiration.

**Usage flow:**
1. Teacher uploads 7 DBQ document images → receives `document_set_id`
2. Teacher grades student essay #1 with `document_set_id` in request
3. Teacher grades students #2-20 using same `document_set_id` (documents cached)
4. Documents auto-expire after 2 hours

**Cost optimization:** Anthropic Prompt Caching can be added to cache the 7 images across multiple grading requests, reducing costs by 90% for batch grading.

---

## Grading Workflow

**Main orchestration** in `app/utils/grading_workflow.py`:

```python
async def grade_essay(
    essay_type: EssayType,
    prompt: str,
    essay_text: Optional[str] = None,
    saq_parts: Optional[Dict[str, str]] = None,
    saq_type: Optional[SAQType] = None,
    rubric_type: Optional[RubricType] = None,
    document_set_id: Optional[str] = None  # NEW: For DBQ with vision
) -> GradeResponse:
    """
    Complete essay grading workflow.

    Steps:
    1. Retrieve documents if document_set_id provided (for DBQ vision)
    2. Validate input (essay_processing.py)
    3. Generate AI prompt (prompt_generation.py)
    4. Call AI service with or without vision (service_locator.py)
    5. Parse response (response_processing.py)
    6. Calculate scores and metrics
    7. Return structured response
    """
```

### Step-by-Step Flow

**1. Essay Processing (`essay_processing.py`)**
```python
# Validate text length, word count
# Extract paragraph count
# Clean whitespace
# Enforce 10,000 word limit
```

**2. Prompt Generation (`prompt_generation.py`)**
```python
# Different prompts for:
# - DBQ (6-point rubric)
# - LEQ (6-point rubric)
# - SAQ College Board (3-point rubric)
# - SAQ EG (10-point A/C/E rubric)

# Includes:
# - Essay type instructions
# - Rubric criteria
# - Expected response format
# - JSON output structure
```

**3. AI Service (`services/ai/`)**
```python
# service_locator.py: Returns mock or real AI
# anthropic_service.py: Claude Sonnet 4 API calls
# mock_service.py: Realistic responses for dev/testing
```

**4. Response Processing (`response_processing.py`)**
```python
# Parse AI JSON response
# Handle both rubric breakdown structures:
# - College Board: part_a/b/c
# - EG: criterion_a/c/e
# - DBQ/LEQ: thesis/evidence/analysis/etc
# Extract scores, feedback, suggestions
```

---

## AI Integration

### Service Locator Pattern

**Why:** Simple way to swap between mock and real AI without code changes.

```python
# Environment variable controls AI service:
AI_SERVICE_TYPE = "mock"       # Default, no API key needed
AI_SERVICE_TYPE = "anthropic"  # Real Claude Sonnet 4

# service_locator.py returns appropriate service
ai_service = get_ai_service()
response = await ai_service.grade_essay(...)
```

### Anthropic Claude Configuration

**Model:** `claude-sonnet-4-5-20250929`

**Why Claude Sonnet 4.5:**
- Most intelligent model for complex reasoning and analysis
- Excellent at structured JSON responses
- Superior historical knowledge and nuanced analysis for APUSH
- Reliable rubric interpretation
- Same cost as Sonnet 4 (~$0.02-0.03 per essay for ≤ 200K token prompts)

**API call structure (text only):**
```python
message = await anthropic_client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=2000,
    temperature=0.3,  # Low for consistency
    system="You are an AP US History grading expert...",
    messages=[{"role": "user", "content": prompt}]
)
```

**API call structure (with vision for DBQ documents):**
```python
# Build content array with images and text
content = []

# Add all 7 documents with labels
for doc in documents:
    content.extend([
        {"type": "text", "text": f"Document {doc['doc_num']}:"},
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": doc["base64"]
            }
        }
    ])

# Add prompt and essay text
content.append({"type": "text", "text": user_message})

message = await anthropic_client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1500,
    temperature=0.3,
    system="You are an AP US History grading expert...",
    messages=[{"role": "user", "content": content}]
)
```

**Vision API features:**
- Supports DBQ essays with document images (charts, graphs, political cartoons)
- Images sent as base64-encoded JPEGs
- Each document labeled (Document 1-7) for student essay references
- Claude reads and analyzes visual content alongside essay text
- Cost: ~$0.02-0.04 per essay with images

**Error handling:**
- Retry on rate limits (3 attempts)
- Fallback to mock on critical failures
- Log all API errors
- User-friendly error messages

### Structured Outputs (Beta)

**Feature:** Anthropic Structured Outputs with constrained decoding
**Status:** ✅ Enabled by default for all essay grading
**SDK Version:** `anthropic==0.63.0`
**API Header:** `anthropic-beta: structured-outputs-2025-11-13`

**How It Works:**

Structured Outputs guarantees 100% schema compliance by using constrained decoding during generation. No more JSON parsing errors or schema validation failures.

1. **Schema Definition** - Pydantic models in `app/models/structured_outputs.py`
2. **API Call** - `client.beta.messages.parse(response_format={"type": schema})`
3. **Guaranteed Compliance** - Constrained decoding ensures exact schema adherence
4. **Grammar Compilation** - First request ~3-5s (cached 24h), subsequent ~1-2s

**Architecture - Two-Schema Approach:**

We maintain separate schemas because Structured Outputs doesn't support `@computed_field`:

- **Output Schemas** (`structured_outputs.py`) - No @computed_field, used for API
  - Plain Pydantic models matching exact JSON structure from Claude
  - 4 essay-specific schemas: DBQ, LEQ, SAQ-College Board, SAQ-EG
  - Factory function: `get_output_schema_for_essay(essay_type, rubric_type)`

- **Core Models** (`core.py`) - With @computed_field (percentage, performance_level)
  - Used throughout application logic
  - Converted from output schemas post-parsing

**Flow:**
```
Claude API → Output Schema (parsed) → Core Model (computed) → Application
```

**API Example:**
```python
from app.models.structured_outputs import get_output_schema_for_essay

# Get schema for essay type
output_schema = get_output_schema_for_essay("DBQ", "college_board")

# Call Structured Outputs API
message = client.beta.messages.parse(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1500,
    temperature=0.3,
    system=system_prompt,
    messages=[{"role": "user", "content": user_message}],
    response_format={"type": output_schema}
)

# Returns parsed Pydantic model (not JSON string!)
parsed_response = message.content  # Already a DBQGradeOutput instance
```

**Benefits:**

- ✅ **Eliminates JSON parsing errors** - No more malformed JSON or extraction failures
- ✅ **Guarantees schema compliance** - 100% adherence to defined structure
- ✅ **Simplified code** - Removed ~100 lines of JSON parsing/validation logic
- ✅ **Type-safe responses** - Pydantic models from the start
- ✅ **No prompt engineering** - No need for JSON formatting instructions in prompts

**Migration Impact:**

- **Removed:** All JSON formatting instructions from prompts (~50 lines per prompt)
- **Removed:** JSON extraction and validation logic from `response_processing.py`
- **Simplified:** `response_processing.py` from ~200 to ~130 lines
- **Updated:** AI service interfaces to return `BaseModel` instead of `str`
- **Updated:** Mock service to return Pydantic models for testing

**Performance:**

- First request: ~3-5 seconds (grammar compilation, cached 24h)
- Subsequent requests: ~1-2 seconds (using cached grammar)
- Cost: Same as regular API calls (~$0.02-0.03 per essay)

---

## Testing Strategy

**51 focused tests** covering core functionality:

### Test Categories

**Integration Tests** (`tests/integration/`)
- Full grading workflow end-to-end
- Mock AI service integration
- Service locator patterns

**Unit Tests** (`tests/`)
- Prompt generation for all essay types
- Response processing for both rubrics
- Essay validation and processing
- Authentication flows
- Rate limiting

**Manual Testing** (`manual_essay_tester.py`)
```bash
# Test with sample essays
python manual_essay_tester.py --sample dbq
python manual_essay_tester.py --sample saq stimulus

# Test with custom essays
python manual_essay_tester.py my_essay.txt dbq my_prompt.txt
```

**Why 51 tests, not 200+:**
- Covers essential paths and edge cases
- Fast execution (< 5 seconds)
- Easy to maintain
- Sufficient for 2-12 teacher scale

---

## Configuration Management

**Pydantic Settings** pattern in `app/config/settings.py`:

```python
class Settings(BaseSettings):
    AI_SERVICE_TYPE: str = "mock"
    ANTHROPIC_API_KEY: Optional[str] = None
    AUTH_PASSWORD: str = "eghsAPUSH"
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:8001",
        "https://apushgrader.vercel.app"
    ]

    class Config:
        env_file = ".env"
```

**Environment Variables:**
- `AI_SERVICE_TYPE`: "mock" or "anthropic"
- `ANTHROPIC_API_KEY`: API key for Claude (required if anthropic)
- `AUTH_PASSWORD`: Teacher password for login
- `ALLOWED_ORIGINS`: CORS origins (comma-separated)

---

## Production Deployment

**Railway.app** hosting:

- **URL:** https://apush-grader-production.up.railway.app
- **Auto-deploy:** Pushes to `main` branch
- **Environment:** Python 3.12, uvicorn ASGI server
- **Config:** Railway environment variables (see above)

**Health monitoring:**
- `GET /health` - Basic health check
- `GET /usage/summary` - Daily usage stats

---

## Code Patterns to Follow

### 1. Model-First Design
Always define Pydantic models before implementing endpoints.

```python
# Good: Type-safe and validated
class GradeRequest(BaseModel):
    essay_type: EssayType
    prompt: str

# Bad: Dict with no validation
def grade_essay(request: dict):
```

### 2. Async/Await Everywhere
All I/O operations are async.

```python
# Good: Non-blocking
async def grade_essay(...) -> GradeResponse:
    response = await ai_service.grade_essay(...)

# Bad: Blocking
def grade_essay(...) -> GradeResponse:
    response = ai_service.grade_essay(...)  # Blocks event loop
```

### 3. Simple Error Handling
User-friendly messages, log details.

```python
try:
    result = await grade_essay(...)
except Exception as e:
    logger.error(f"Grading failed: {str(e)}")
    raise HTTPException(
        status_code=500,
        detail="Essay grading failed. Please try again."
    )
```

### 4. Direct Utility Functions
No complex dependency injection.

```python
# Good: Simple function calls
from app.utils.grading_workflow import grade_essay
result = await grade_essay(...)

# Bad: Over-engineered DI
result = await container.get(IGradingService).grade(...)
```

---

## Future Features to Implement

### 1. Custom LEQ Rubrics
**Status:** Planned

**Current:** LEQ uses standard College Board 6-point rubric
**Needed:** Teachers want custom rubrics with different criteria/weights

**Implementation approach:**
1. Add `RubricType` enum for LEQ (like SAQ has)
2. Store custom rubrics in JSON files or env config
3. Update `prompt_generation.py` to use custom rubric
4. Update `response_processing.py` to parse custom breakdown
5. Add validation for custom rubric structure

**Example custom rubric:**
```json
{
  "rubric_name": "EG LEQ Rubric",
  "max_score": 10,
  "criteria": [
    {"name": "thesis", "points": 2, "description": "..."},
    {"name": "evidence", "points": 4, "description": "..."},
    {"name": "analysis", "points": 4, "description": "..."}
  ]
}
```

### 2. Image Upload for DBQ
**Status:** ✅ Implemented (Phase 1 Complete)

**Implementation:**
- New endpoint: `POST /api/v1/dbq/documents` for uploading 7 JPEG documents
- Vision API integration using Anthropic Claude's native vision capabilities
- No OCR needed - Claude reads images directly (charts, graphs, political cartoons, text)
- Session-based document storage with 2-hour expiration
- Documents cached for batch grading cost optimization

**Completed features:**
- Upload 7 DBQ document images
- Store documents in session cache
- Pass `document_set_id` in grading requests
- Claude Vision API integration in `anthropic_service.py`
- Mock service support for testing

**Remaining work (Phase 2-4):**
- Frontend document upload component
- Anthropic Prompt Caching for 90% cost reduction
- Image compression/resizing
- Integration tests

### 3. Verify Claude Model Version
**Status:** ✅ Complete

**Current:** Using `claude-sonnet-4-5-20250929` (Sonnet 4.5)
**Previous:** `claude-sonnet-4-20250514` (Sonnet 4)

**Upgrade Benefits:**
- Most intelligent model for complex reasoning and analysis
- Same cost as Sonnet 4 for prompts ≤ 200K tokens
- Superior performance on nuanced historical analysis
- Better rubric adherence and feedback quality

**Verified:** 2025-10-16 via https://docs.claude.com/en/docs/about-claude/models

---

## Common Development Tasks

### Adding a New Essay Type
1. Add to `EssayType` enum in `models/core.py`
2. Create prompt template in `prompt_generation.py`
3. Add response parser in `response_processing.py`
4. Update `GradeRequest` validation in `requests/grading.py`
5. Add sample essay to `sample_essays/`
6. Write integration test

### Adding a New Rubric
1. Add to `RubricType` enum in `models/core.py`
2. Create rubric-specific prompt in `prompt_generation.py`
3. Add breakdown parser in `response_processing.py`
4. Update frontend rubric selector
5. Add sample test cases
6. Update documentation

### Debugging Grading Issues
1. Check logs for AI service errors
2. Use `manual_essay_tester.py` to isolate issue
3. Examine AI response JSON structure
4. Verify prompt includes all rubric criteria
5. Test with mock AI to rule out API issues

---

## Key Files Reference

| File | Purpose | When to Edit |
|------|---------|--------------|
| `app/main.py` | FastAPI app setup | Adding middleware, CORS origins |
| `app/models/core.py` | Core enums and models | Adding essay types, rubrics |
| `app/api/routes/grading.py` | Grading endpoint | Changing API contract |
| `app/api/routes/dbq.py` | DBQ document upload | Changing document requirements, storage |
| `app/utils/grading_workflow.py` | Main orchestration | Modifying grading flow |
| `app/utils/prompt_generation.py` | AI prompts | Improving rubric instructions |
| `app/utils/response_processing.py` | Parse AI output | Handling new response formats |
| `app/services/ai/anthropic_service.py` | Anthropic Claude API | Adding vision support, caching |
| `app/services/ai/service_locator.py` | AI service factory | Adding new AI providers |
| `app/config/settings.py` | Environment config | Adding new config options |

---

## Quick Reference

**Start server:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Run tests:**
```bash
pytest tests/ -v
```

**Manual testing:**
```bash
python manual_essay_tester.py --sample saq
```

**API docs:**
- Interactive: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Production:**
- API: https://apush-grader-production.up.railway.app
- Docs: https://apush-grader-production.up.railway.app/docs
