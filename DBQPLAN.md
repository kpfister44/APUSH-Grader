# DBQ Document Upload Implementation Plan

**Goal:** Add full support for DBQ essays with image document uploads using Claude's Vision API

**Key Innovation:** Use Anthropic Prompt Caching to reuse 7 documents across 20 students (90%+ cost reduction)

---

## Overview

### Current State
- DBQ and LEQ are nearly identical (both use text-only prompts)
- No support for uploading document images
- Teachers must type/paste document content

### Target State
- Teachers upload 7 PNG screenshots once per assignment
- Documents cached for batch grading session (2 hours)
- Claude Vision API reads charts, graphs, political cartoons, text
- Reuse documents across 20+ student essays (major cost savings)

---

## Technical Requirements

### File Format
- **PNG only** (native Mac screenshot format)
- Always 7 documents (Document 1-7)
- Max 5MB per image (Claude API limit)
- Documents labeled by number (students reference "Document 1", "Document 2", etc.)

### Storage Strategy
- **Session-based caching** (in-memory, like current auth sessions)
- 2-hour expiration (perfect for batch grading)
- No persistent storage needed (can upgrade to SQLite/S3 later if needed)

### Cost Optimization
- **Anthropic Prompt Caching** - Cache 7 images + rubric instructions
- Only pay full price for first student, cache hits for remaining 19
- Estimated 90%+ cost reduction for batch grading

---

## Architecture Design

### Two-Endpoint Approach

**1. Upload Documents (Once per assignment)**
```
POST /api/v1/dbq/documents
Request: 7 PNG files
Response: {document_set_id, document_count, expires_at}
```

**2. Grade Essay (Multiple times with same documents)**
```
POST /api/v1/grade
Request: {essay_type: "DBQ", document_set_id, prompt, essay_text}
Response: Standard GradeResponse with scores/feedback
```

### User Flow
1. Teacher selects DBQ essay type
2. Upload 7 document screenshots → Receive `document_set_id`
3. Enter DBQ question prompt
4. Enter student essay #1 → Grade (full vision API call)
5. Enter student essay #2 → Grade (cached documents, only essay changes)
6. Repeat for students 3-20 (all use cached documents)

---

## Implementation Phases

### Phase 1: Basic Vision Support (MVP)
**Goal:** Get document upload + vision API working end-to-end

**Backend Tasks:**
- [x] Create new models in `backend/app/models/requests/grading.py`
  - `DocumentUploadRequest`
  - `DocumentUploadResponse`
  - Update `GradeRequest` to include `document_set_id`
- [x] Create new route `backend/app/api/routes/dbq.py`
  - `POST /api/v1/dbq/documents` endpoint
  - Validate 7 PNGs, < 5MB each
  - Convert to base64
  - Store in session cache (like auth tokens)
- [x] Update `backend/app/utils/grading_workflow.py`
  - Add `document_set_id` parameter
  - Retrieve documents from cache
  - Pass to AI service
- [x] Update `backend/app/services/ai/anthropic_service.py`
  - New method: `grade_dbq_with_documents()`
  - Build multi-part content array (images + text)
  - Use Claude Vision API format
- [x] Test with sample DBQ essay

**Estimated effort:** 4-6 hours

---

### Phase 2: Frontend Integration
**Goal:** Allow teachers to upload documents and grade students

**Frontend Tasks:**
- [ ] Create `webfrontend/src/components/DocumentUpload.tsx`
  - 7 file input fields (Document 1-7)
  - Upload button
  - Preview uploaded images
  - Display `document_set_id` after upload
- [ ] Update grading context to store `document_set_id`
- [ ] Update grading form to include `document_set_id` in request
- [ ] Add "Clear Documents" button (reset for new assignment)
- [ ] Show document thumbnails during grading

**Estimated effort:** 3-4 hours

---

### Phase 3: Prompt Caching Optimization (Optional but Recommended)
**Goal:** Reduce costs by 90% for batch grading

**Tasks:**
- [ ] Implement Anthropic prompt caching in `anthropic_service.py`
  - Add `cache_control: {"type": "ephemeral"}` to documents
  - Mark rubric as cacheable
  - Keep student essay uncached (changes per request)
- [ ] Test cache hit rates with multiple essays
- [ ] Add cache metrics to `/usage/summary` endpoint
- [ ] Monitor cost savings in production

**Reference:** https://docs.anthropic.com/en/docs/prompt-caching

**Estimated effort:** 2-3 hours

---

### Phase 4: Polish
**Goal:** Production-ready with error handling and optimizations

**Tasks:**
- [ ] Image compression/resizing (if needed for cost control)
- [ ] Better error messages:
  - File too large
  - Wrong format (not PNG)
  - Not exactly 7 files
  - Document set expired
- [ ] Add document expiration warnings (e.g., "Documents expire in 30 minutes")
- [ ] Write integration tests for vision grading workflow
- [ ] Update `backend/BACKEND.md` with vision API documentation
- [ ] Add sample DBQ essays to `backend/sample_essays/`

**Estimated effort:** 2-3 hours

---

## Technical Details

### Backend Models

```python
# backend/app/models/requests/grading.py

class DocumentUploadRequest(BaseModel):
    """Upload 7 DBQ document images"""
    documents: List[UploadFile]  # Exactly 7 PNGs
    assignment_name: Optional[str] = None

class DocumentUploadResponse(BaseModel):
    document_set_id: str
    document_count: int
    total_size_mb: float
    expires_at: datetime

class GradeRequest(BaseModel):
    essay_type: EssayType
    prompt: str
    essay_text: Optional[str] = None
    saq_parts: Optional[Dict[str, str]] = None
    saq_type: Optional[SAQType] = None
    rubric_type: Optional[RubricType] = None
    document_set_id: Optional[str] = None  # NEW: For DBQ only
```

### Storage Structure

```python
# In-memory cache (like current auth sessions)
document_sets = {
    "uuid-1234": {
        "documents": [
            {"doc_num": 1, "base64": "...", "size_bytes": 123456},
            {"doc_num": 2, "base64": "...", "size_bytes": 234567},
            # ... 7 total
        ],
        "uploaded_at": datetime,
        "expires_at": datetime,
        "assignment_name": "DBQ Unit 5"
    }
}
```

### Anthropic Vision API Format

**Without Prompt Caching:**
```python
content = []

# Add all 7 documents
for doc in documents:
    content.extend([
        {"type": "text", "text": f"Document {doc['doc_num']}:"},
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": doc['base64']
            }
        }
    ])

# Add prompt and essay
content.extend([
    {"type": "text", "text": f"DBQ Question: {prompt}"},
    {"type": "text", "text": f"Student Essay: {essay_text}"},
    {"type": "text", "text": "Grade according to DBQ rubric..."}
])

message = await anthropic_client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2000,
    messages=[{"role": "user", "content": content}]
)
```

**With Prompt Caching (Phase 3):**
```python
content = []

# Add documents (cacheable)
for doc in documents:
    content.extend([
        {"type": "text", "text": f"Document {doc['doc_num']}:"},
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": doc['base64']
            }
        }
    ])

# Mark rubric as end of cached content
content.append({
    "type": "text",
    "text": "Rubric: [DBQ rubric details...]",
    "cache_control": {"type": "ephemeral"}  # Cache everything above
})

# Student essay NOT cached (changes per request)
content.extend([
    {"type": "text", "text": f"Student Essay: {essay_text}"},
    {"type": "text", "text": "Grade this essay..."}
])
```

---

## Cost Analysis

### Without Caching
- 7 images × 20 students = 140 image API calls
- ~$0.02/essay × 20 = $0.40 total

### With Caching
- 7 images × 1 cache creation = 7 full-price calls
- 19 cache hits = 90% cost reduction
- ~$0.02 first essay + $0.002 × 19 = ~$0.06 total
- **Savings: $0.34 (85% reduction for 20 students)**

For a teacher grading 100 DBQs per year: **$17 savings** (meaningful at hobby project scale)

---

## Testing Strategy

### Manual Testing
```bash
# Upload 7 test documents
curl -X POST http://localhost:8000/api/v1/dbq/documents \
  -F "documents=@doc1.jpg" \
  -F "documents=@doc2.jpg" \
  # ... all 7

# Grade with document_set_id
curl -X POST http://localhost:8000/api/v1/grade \
  -H "Content-Type: application/json" \
  -d '{
    "essay_type": "DBQ",
    "document_set_id": "uuid-1234",
    "prompt": "Evaluate the extent...",
    "essay_text": "Student essay here..."
  }'
```

### Integration Tests
```python
# tests/integration/test_dbq_vision.py
async def test_upload_documents():
    """Test document upload endpoint"""

async def test_grade_with_documents():
    """Test grading with document_set_id"""

async def test_document_expiration():
    """Test documents expire after 2 hours"""

async def test_invalid_document_count():
    """Test error when not exactly 7 documents"""
```

---

## Future Enhancements (Post-Launch)

1. **Persistent Storage** - Move from in-memory to SQLite/S3 for multi-day persistence
2. **Document Preview in Results** - Show which document student referenced
3. **OCR Fallback** - Extract text from images for search/analysis
4. **PDF Support** - Upload single PDF with all 7 documents
5. **Automatic Document Labeling** - Use Claude to auto-number documents
6. **Document Library** - Save common DBQ sets for reuse across years

---

## Success Criteria

### Phase 1 Complete When:
- [x] Teacher can upload 7 PNGs via API
- [x] Documents stored in session cache
- [x] Claude Vision API successfully reads documents
- [x] Grading returns accurate scores/feedback
- [x] Works with mock AI service for testing

### Phase 2 Complete When:
- [x] Frontend upload component works
- [x] Teacher can grade 20 students without re-uploading
- [x] Document thumbnails visible during grading
- [x] Clear error messages for invalid uploads

### Phase 3 Complete When:
- [ ] Prompt caching reduces costs by 80%+
- [ ] Cache hit rate tracked in metrics
- [ ] No quality degradation from caching

### Production Ready When:
- [ ] All 4 phases complete
- [ ] Integration tests passing
- [ ] Deployed to Railway + Vercel
- [ ] Tested with real DBQ documents
- [ ] Documentation updated

---

## Resources

- **Anthropic Vision API**: https://docs.anthropic.com/en/docs/vision
- **Prompt Caching**: https://docs.anthropic.com/en/docs/prompt-caching
- **Claude Sonnet 4 Pricing**: https://docs.anthropic.com/en/docs/pricing
- **College Board DBQ Rubric**: https://apcentral.collegeboard.org/

---

## Questions/Decisions

- [x] PNG vs JPEG vs PDF? → **PNG** (native Mac screenshot format)
- [x] Claude Vision vs OCR? → **Claude Vision** (preserves visual context)
- [x] Storage approach? → **Session-based** (2-hour expiration, perfect for batch grading)
- [x] Always 7 documents? → **Yes** (standard DBQ format)
- [x] Cost optimization? → **Prompt Caching** (90%+ savings for batch grading)

---

**Last Updated:** 2025-10-15
**Status:** Phase 1 - Complete ✅ | Phase 2 - Complete ✅ | Phase 3 - Ready to Start
