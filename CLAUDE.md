# CLAUDE.md

**High-level guidance for Claude Code when working with this repository.**

**📚 For detailed architecture and patterns, see:**
- **Backend:** [`backend/BACKEND.md`](backend/BACKEND.md) - FastAPI architecture, models, AI integration
- **Frontend:** [`webfrontend/FRONTEND.md`](webfrontend/FRONTEND.md) - React components, state management, styling

---

## Project Overview

**APUSH Grader** - AI essay grading system with Python FastAPI backend + ChatGPT-style web frontend. Uses Anthropic Claude Sonnet 4 to grade AP US History essays (DBQ/LEQ/SAQ) based on College Board rubrics.

**Target Audience:** 2-12 teachers (hobby project scale)
**Philosophy:** Simplicity over complexity - functionality over comprehensiveness

## Current Status

- ✅ **Backend**: Production on Railway (https://apush-grader-production.up.railway.app)
- ✅ **Frontend**: Production on Vercel (https://apushgrader.vercel.app)
- ✅ **Authentication**: Password-protected teacher access (`eghsAPUSH`)
- ✅ **Dual SAQ Rubrics**: College Board (3-point) + EG (10-point A/C/E)

## Quick Tech Stack

**Backend:** Python 3.12, FastAPI 0.104.1, Anthropic 0.57.1, Pydantic 2.5.0
**Frontend:** React 19.1.0, TypeScript 5.8.3, Tailwind CSS 4.1.11, ESBuild 0.25.8
**Testing:** Pytest (51 backend tests)
**Deployment:** Railway (backend) + Vercel (frontend)

## Repository Structure

```
APUSH-Grader/
├── backend/              # Python FastAPI backend
│   ├── BACKEND.md       # 📚 Detailed backend architecture docs
│   ├── app/             # Application code
│   └── tests/           # 51 focused tests
├── webfrontend/         # React/TypeScript frontend
│   ├── FRONTEND.md      # 📚 Detailed frontend architecture docs
│   └── src/             # React components, contexts, services
├── CLAUDE.md            # This file (high-level guidance)
└── README.md            # User-facing documentation
```

## Quick Commands

```bash
# Backend
cd backend && source venv/bin/activate
uvicorn app.main:app --reload          # http://localhost:8000
pytest tests/ -v                        # Run tests

# Frontend
cd webfrontend
npm run dev                             # http://127.0.0.1:8001

# Manual testing
python backend/manual_essay_tester.py --sample saq
```

## Key Features

**Essay Types:** DBQ (6pt), LEQ (6pt), SAQ (3pt or 10pt)
**Dual SAQ Rubrics:** College Board (3-point A/B/C) + EG (10-point A/C/E criteria)
**Authentication:** Password-protected (`eghsAPUSH`)
**AI:** Anthropic Claude Sonnet 4 (~$0.02/essay) with mock mode for dev
**Rate Limits:** 20 req/min, 50 essays/hour, 50/day

## Code Documentation Philosophy

**Comment on "why," not "what"** - Explain design decisions, not functionality.

**❌ Bad:** `# This function splits data into chunks and multiplies`
**✅ Good:** `# Split required due to API 10K word limit per request`

**Document:**
- Design decisions and constraints
- Historical context ("This works around X API limitation")
- Future considerations ("When Y is available, consider Z")
- Critical failure modes

**Don't document:**
- Obvious functionality
- Self-evident implementation details

## Git Workflow

**Feature branch workflow required:**

```bash
# Create feature branch
git checkout -b feature/issue-number-description

# Commit with clear message
git commit -m "[BACKEND] Add custom LEQ rubric support"
git commit -m "[FRONTEND] Add image upload component"

# Push and create PR
git push -u origin feature/issue-number-description
gh pr create --title "[AREA] Brief description" --body "Details"
gh pr merge --squash --delete-branch
```

## Production URLs

- **🌐 App**: https://apushgrader.vercel.app (password: `eghsAPUSH`)
- **🔧 API**: https://apush-grader-production.up.railway.app
- **📚 Docs**: https://apush-grader-production.up.railway.app/docs

**Deployment:**
- Backend: Railway (auto-deploy from `main`)
- Frontend: Vercel (auto-deploy from `main`)

## Environment Configuration

**Backend** (`backend/.env`):
```bash
AI_SERVICE_TYPE=mock              # or "anthropic" for production
ANTHROPIC_API_KEY=sk-ant-...      # Required for production
AUTH_PASSWORD=eghsAPUSH           # Teacher password
```

**Frontend** (production URL hardcoded due to ESBuild env var issues):
- Dev: `http://localhost:8000` (backend)
- Prod: `https://apush-grader-production.up.railway.app`

## Tailwind CSS v4 Patterns

**✅ Working patterns:**
```css
bg-orange-500 hover:bg-orange-600
text-gray-800 rounded-2xl shadow-sm
p-10 space-y-8 max-w-4xl
```

**❌ Broken in v4 (don't use):**
```css
text-white/95                    /* Opacity shortcuts */
bg-linear-to-r from-orange-500   /* Gradients */
```

**After adding new classes:** Run `npm run build:css`

## Future Features (Planned)

1. **Custom LEQ Rubrics** - Teachers define custom criteria/weights
2. **Image Upload for DBQ** - OCR scanned documents (needs backend OCR)
3. **Verify Claude Model** - Ensure using latest Sonnet 4 version

See `backend/BACKEND.md` and `webfrontend/FRONTEND.md` for implementation details.