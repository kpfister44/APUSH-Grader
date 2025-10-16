# Frontend Architecture Documentation

**React/TypeScript Web Frontend for APUSH Grader**

This document provides architectural context for Claude Code to understand the frontend system quickly and begin development work.

## Core Philosophy

**ChatGPT-inspired interface** with modern web patterns for 2-12 teachers.

### Key Decisions
- **React 19** with functional components and hooks
- **TypeScript** for type safety and better DX
- **React Context** for state management (no Redux complexity)
- **Tailwind CSS v4** for utility-first styling
- **ESBuild** for fast builds and hot reloading
- **No framework overhead** - just React Router for navigation

**Why:** Teachers need a familiar, fast, mobile-responsive interface that "just works."

---

## Project Structure

```
webfrontend/
├── src/
│   ├── index.tsx                   # Entry point, React render
│   ├── App.tsx                     # Root component, routing, auth wrapper
│   ├── components/
│   │   ├── auth/
│   │   │   └── LoginScreen.tsx    # Password authentication UI
│   │   ├── input/
│   │   │   ├── EssayTypeSelector.tsx    # DBQ/LEQ/SAQ selector
│   │   │   ├── SAQTypeSelector.tsx      # Stimulus/NonStimulus/Secondary
│   │   │   ├── RubricTypeSelector.tsx   # College Board vs EG
│   │   │   ├── PromptInput.tsx          # Question text input
│   │   │   ├── SAQMultiPartInput.tsx    # Part A/B/C inputs
│   │   │   └── ChatTextArea.tsx         # Main essay input
│   │   ├── ui/
│   │   │   ├── ResultsDisplay.tsx       # Grading results layout
│   │   │   ├── ScoreVisualizer.tsx      # Score charts/progress bars
│   │   │   ├── SubmitButton.tsx         # Grade essay button
│   │   │   └── ValidationFeedback.tsx   # Error/warning messages
│   │   └── pdf/
│   │       └── PDFExport.tsx            # PDF generation (@react-pdf/renderer)
│   ├── contexts/
│   │   ├── AuthContext.tsx             # Authentication state
│   │   └── GradingContext.tsx          # Essay grading state
│   ├── services/
│   │   └── api.ts                      # Backend API client
│   ├── types/
│   │   ├── api.ts                      # Backend API types
│   │   ├── ui.ts                       # UI-specific types
│   │   └── index.ts                    # Re-exports
│   ├── pages/
│   │   ├── GradingPage.tsx             # Main grading interface
│   │   └── LoginPage.tsx               # Login screen
│   └── styles/
│       └── index.css                   # Tailwind imports + custom CSS
├── build.js                            # ESBuild configuration
├── package.json                        # Dependencies
└── vercel.json                         # Vercel deployment config
```

---

## Tech Stack Details

### React 19.1.0
- **Functional components** with hooks (no class components)
- **useEffect** for side effects
- **useMemo/useCallback** for performance
- **Custom hooks** for reusable logic

### TypeScript 5.8.3
- **Strict mode** enabled for type safety
- **Interface-first design** - define types before implementing
- **No `any` types** unless absolutely necessary
- **Type inference** where possible

### React Router DOM 7.7.0
- **Client-side routing** for SPA navigation
- **Nested routes** for auth-protected pages
- **URL state management** (future: deep linking to results)

### Tailwind CSS 4.1.11
**Important:** v4.x has breaking changes from v3.x

**Working patterns:**
- `bg-orange-500 hover:bg-orange-600` ✅
- `text-gray-800` ✅
- `rounded-2xl shadow-sm` ✅

**Don't use (broken in v4):**
- `bg-linear-to-r from-orange-500` ❌
- `text-white/95` (opacity shortcuts) ❌
- `border-gray-100/80` ❌

**Build process:**
```bash
npm run build:css  # Generate CSS from Tailwind classes
npm run dev        # Watch mode with hot reload
```

### ESBuild 0.25.8
- **Fast bundling** (~50ms rebuild)
- **Hot reloading** in development
- **CSS watching** with Tailwind
- **Custom build script** in `build.js`

### @react-pdf/renderer 4.3.0
- **Client-side PDF generation** (no backend needed)
- **React components** for PDF layout
- **Export grading results** as PDF for record-keeping

---

## State Management

**React Context pattern** - no Redux, MobX, or Zustand complexity.

### AuthContext (`src/contexts/AuthContext.tsx`)

**Purpose:** Manage authentication state across the app.

```typescript
interface AuthContextType {
  isAuthenticated: boolean;
  token: string | null;
  login: (password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  error: string | null;
}
```

**Key features:**
- Session token stored in localStorage
- Auto-logout on token expiry
- Loading states for login flow
- Error handling for failed auth

**Usage:**
```typescript
const { isAuthenticated, login, logout } = useAuth();

if (!isAuthenticated) {
  return <LoginPage />;
}
```

### GradingContext (`src/contexts/GradingContext.tsx`)

**Purpose:** Manage essay grading workflow state.

```typescript
interface GradingContextType {
  // Form state
  essayType: EssayType;
  saqType: SAQType | null;
  rubricType: RubricType | null;
  prompt: string;
  essayText: string;
  saqParts: { part_a: string; part_b: string; part_c: string };

  // Grading state
  isGrading: boolean;
  result: GradeResponse | null;
  error: string | null;

  // Actions
  setEssayType: (type: EssayType) => void;
  setSAQType: (type: SAQType) => void;
  setRubricType: (type: RubricType) => void;
  setPrompt: (text: string) => void;
  setEssayText: (text: string) => void;
  setSAQParts: (parts: SAQParts) => void;
  submitForGrading: () => Promise<void>;
  resetForm: () => void;
}
```

**Key features:**
- Centralized form state
- Validation before submission
- Loading states during grading
- Error handling with user-friendly messages
- Form reset after successful grading

**Dynamic field visibility:**
```typescript
// SAQ-specific fields only show when essay_type = SAQ
{essayType === 'SAQ' && (
  <>
    <SAQTypeSelector />
    <RubricTypeSelector />
    <SAQMultiPartInput />
  </>
)}
```

---

## Component Architecture

### Component Patterns

**1. Input Components** (`components/input/`)

All input components follow this pattern:
```typescript
interface Props {
  value: string | EssayType | etc;
  onChange: (value: string | EssayType | etc) => void;
  disabled?: boolean;
  error?: string;
}

export function InputComponent({ value, onChange, disabled, error }: Props) {
  // Controlled component pattern
  // Tailwind styling
  // Accessibility (aria-labels, keyboard nav)
}
```

**2. Display Components** (`components/ui/`)

Display components are presentational:
```typescript
interface Props {
  data: GradeResponse;
  onExport?: () => void;
}

export function DisplayComponent({ data, onExport }: Props) {
  // No state management
  // Pure presentation
  // Responsive design (mobile-first)
}
```

**3. Container Components** (Pages)

Pages connect state to UI:
```typescript
export function GradingPage() {
  const grading = useGrading();
  const auth = useAuth();

  return (
    <>
      <InputComponents {...grading} />
      <ResultsDisplay result={grading.result} />
    </>
  );
}
```

### Key Components

#### EssayTypeSelector
**Purpose:** Choose DBQ, LEQ, or SAQ

**Key features:**
- Large clickable cards
- Visual icons/indicators
- Shows selected state
- Triggers conditional field rendering

#### SAQMultiPartInput
**Purpose:** Input for SAQ part A, B, and C

**Key features:**
- Three separate text areas
- Labels for each part
- Character count per part
- Individual validation

**Why separate:** SAQ grading evaluates each part independently.

#### RubricTypeSelector
**Purpose:** Choose College Board vs EG rubric (SAQ only)

**Key features:**
- Only visible for SAQ essays
- Explains rubric differences
- Default to College Board

**Why needed:** Dual rubric support (see backend docs).

#### ResultsDisplay
**Purpose:** Show grading results after submission

**Key features:**
- Score visualization (pie chart, progress bar)
- Breakdown by rubric criteria
- Overall feedback section
- Suggestions list
- PDF export button

**Layout:** Follows ChatGPT message style (assistant message with structured content).

#### PDFExport
**Purpose:** Generate PDF of grading results

**Implementation:**
```typescript
import { Document, Page, Text, View } from '@react-pdf/renderer';

const GradingPDF = ({ result }: { result: GradeResponse }) => (
  <Document>
    <Page>
      <View>
        <Text>Score: {result.score}/{result.max_score}</Text>
        {/* Structured layout of all grading data */}
      </View>
    </Page>
  </Document>
);

// Usage:
<PDFDownloadLink document={<GradingPDF result={result} />} fileName="grade.pdf">
  Download PDF
</PDFDownloadLink>
```

---

## API Integration

**Backend API client** in `src/services/api.ts`:

### API Configuration

```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL ||
  (process.env.NODE_ENV === 'production'
    ? 'https://apush-grader-production.up.railway.app'
    : 'http://localhost:8000');
```

**Note:** ESBuild environment variable injection has issues, so production URL is hardcoded as fallback.

### API Methods

```typescript
// Authentication
export async function login(password: string): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password })
  });

  if (!response.ok) {
    throw new Error('Login failed');
  }

  return response.json();
}

// Grading
export async function gradeEssay(
  request: GradeRequest,
  token: string
): Promise<GradeResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/grade`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Grading failed');
  }

  return response.json();
}
```

### Error Handling

```typescript
try {
  const result = await gradeEssay(request, token);
  setResult(result);
} catch (error) {
  if (error instanceof Error) {
    setError(error.message);
  } else {
    setError('An unexpected error occurred');
  }
} finally {
  setIsGrading(false);
}
```

---

## Styling Patterns

**Tailwind CSS v4** utility-first approach:

### Layout Patterns

**Page layout:**
```tsx
<div className="min-h-screen bg-gray-50 py-16 px-6">
  <div className="max-w-4xl mx-auto space-y-8">
    {/* Content */}
  </div>
</div>
```

**Card layout:**
```tsx
<div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-10">
  {/* Card content */}
</div>
```

**Button styling:**
```tsx
<button className="w-full py-4 px-8 bg-orange-500 hover:bg-orange-600 text-white rounded-xl font-medium">
  Grade Essay
</button>
```

### Typography

```css
/* Headers */
text-4xl font-normal mb-16      /* Page titles */
text-2xl font-medium mb-6       /* Section headers */
text-xl font-light mb-4         /* Subtitles */

/* Body text */
text-base font-normal           /* Regular text */
text-sm text-gray-600           /* Secondary text */
```

### Spacing

```css
/* Sections */
space-y-8                       /* Vertical spacing between sections */
mb-16 mt-8                      /* Large section breaks */

/* Components */
p-10                            /* Card padding */
py-4 px-8                       /* Button padding */
```

### Colors

**Primary (orange):**
- `bg-orange-500` - Primary actions
- `hover:bg-orange-600` - Hover states
- `text-orange-600` - Accent text

**Neutrals:**
- `bg-gray-50` - Page background
- `bg-white` - Card background
- `text-gray-800` - Headers
- `text-gray-600` - Body text
- `border-gray-200` - Dividers

### Responsive Design

**Mobile-first approach:**
```tsx
<div className="
  grid grid-cols-1          /* Mobile: 1 column */
  md:grid-cols-2            /* Tablet: 2 columns */
  lg:grid-cols-3            /* Desktop: 3 columns */
  gap-4
">
```

**Common breakpoints:**
- `sm:` - 640px (mobile landscape)
- `md:` - 768px (tablet)
- `lg:` - 1024px (desktop)
- `xl:` - 1280px (large desktop)

---

## Authentication Flow

**Session-based with token storage:**

### Login Flow

1. **User enters password** on LoginScreen
2. **Frontend calls** `POST /auth/login`
3. **Backend returns** `{ token, expires_at }`
4. **Frontend stores** token in localStorage
5. **Frontend sets** AuthContext.isAuthenticated = true
6. **App redirects** to GradingPage

### Protected Routes

```tsx
function App() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={isAuthenticated ? <GradingPage /> : <Navigate to="/login" />}
      />
    </Routes>
  );
}
```

### Token Persistence

```typescript
// Save token on login
localStorage.setItem('auth_token', token);
localStorage.setItem('token_expires', expiresAt);

// Restore on page load
useEffect(() => {
  const token = localStorage.getItem('auth_token');
  const expires = localStorage.getItem('token_expires');

  if (token && expires && new Date(expires) > new Date()) {
    setToken(token);
    setIsAuthenticated(true);
  }
}, []);

// Clear on logout
localStorage.removeItem('auth_token');
localStorage.removeItem('token_expires');
```

---

## Build and Deployment

### Development

```bash
npm run dev
# Starts ESBuild dev server at http://127.0.0.1:8001
# Hot reload enabled
# CSS watching active
```

### Production Build

```bash
npm run build
# ESBuild bundles to /dist
# Minified and optimized
# Tailwind CSS generated
```

### Vercel Deployment

**Auto-deploy** from `main` branch:
- **URL:** https://apushgrader.vercel.app
- **Config:** `vercel.json` with ESBuild settings
- **Environment:** Node.js 18.x
- **Build command:** `npm run build`
- **Output:** `/dist` directory

**vercel.json:**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": null
}
```

---

## Type Definitions

**Shared types** between frontend and backend:

### API Types (`src/types/api.ts`)

```typescript
// Match backend models exactly
export type EssayType = 'DBQ' | 'LEQ' | 'SAQ';

export type SAQType = 'stimulus' | 'non_stimulus' | 'secondary_comparison';

export type RubricType = 'college_board' | 'eg';

export interface GradeRequest {
  essay_type: EssayType;
  prompt: string;
  essay_text?: string;
  saq_parts?: {
    part_a: string;
    part_b: string;
    part_c: string;
  };
  saq_type?: SAQType;
  rubric_type?: RubricType;
}

export interface GradeResponse {
  score: number;
  max_score: number;
  percentage: number;
  letter_grade: string;
  performance_level: string;
  breakdown: {
    [key: string]: {
      score: number;
      max_score?: number;
      feedback: string;
    };
  };
  overall_feedback: string;
  suggestions: string[];
  word_count: number;
  paragraph_count: number;
}
```

**Important:** Keep types in sync with backend Pydantic models.

---

## Future Features to Implement

### 1. Image Upload for DBQ
**Status:** Planned

**Current:** Text-based prompt and essay input
**Needed:** Upload scanned/photographed DBQ documents

**Implementation approach:**

**1. Add file input component:**
```tsx
export function DocumentUpload({ onChange }: { onChange: (files: File[]) => void }) {
  return (
    <input
      type="file"
      multiple
      accept="image/*,application/pdf"
      onChange={(e) => onChange(Array.from(e.target.files || []))}
    />
  );
}
```

**2. Update GradingContext:**
```typescript
interface GradingContextType {
  // Add document files
  documents: File[];
  setDocuments: (files: File[]) => void;
}
```

**3. Update API client:**
```typescript
export async function gradeEssayWithDocuments(
  request: GradeRequest,
  documents: File[],
  token: string
): Promise<GradeResponse> {
  const formData = new FormData();
  formData.append('request', JSON.stringify(request));
  documents.forEach((doc, i) => {
    formData.append(`document_${i}`, doc);
  });

  const response = await fetch(`${API_BASE_URL}/api/v1/grade`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  });

  return response.json();
}
```

**4. UI considerations:**
- Thumbnail previews of uploaded documents
- Drag-and-drop upload area
- Progress indicator during upload
- OCR processing status
- Fallback to manual text entry

**Backend dependency:** Backend must implement OCR and multipart/form-data handling.

### 2. Deep Linking to Results
**Status:** Potential enhancement

**Idea:** Share grading results via URL

**Implementation:**
```typescript
// Save result to URL params
const resultId = generateResultId();
localStorage.setItem(resultId, JSON.stringify(result));
navigate(`/results/${resultId}`);

// Restore from URL
const { resultId } = useParams();
const savedResult = localStorage.getItem(resultId);
```

**Benefits:** Teachers can bookmark specific grading results for later review.

### 3. Grading History
**Status:** Potential enhancement

**Idea:** Keep history of graded essays

**Implementation:**
```typescript
interface GradingHistory {
  id: string;
  timestamp: Date;
  essayType: EssayType;
  score: number;
  result: GradeResponse;
}

// Store in localStorage
const history: GradingHistory[] = JSON.parse(
  localStorage.getItem('grading_history') || '[]'
);
```

**UI:** Sidebar with list of previous gradings, click to view results.

---

## Common Development Tasks

### Adding a New Input Component

1. Create component in `src/components/input/`
2. Define props interface with `value` and `onChange`
3. Use controlled component pattern
4. Add Tailwind styling (follow existing patterns)
5. Add to GradingContext if needed
6. Import in GradingPage

### Updating API Types

1. Check backend changes in `backend/app/models/`
2. Update `src/types/api.ts` to match
3. Update API client methods in `src/services/api.ts`
4. Update GradingContext state if needed
5. Test with real backend

### Styling a New Component

1. Use existing Tailwind patterns (see "Styling Patterns" above)
2. Test on mobile, tablet, desktop
3. Run `npm run build:css` to generate classes
4. Check hover/focus states
5. Verify accessibility (keyboard nav, screen readers)

### Debugging API Issues

1. Check browser DevTools Network tab
2. Verify request payload matches backend expectations
3. Check authentication token is included
4. Test backend endpoint directly (Postman, curl)
5. Check CORS configuration in backend

---

## Code Quality Standards

### TypeScript
- **No `any` types** - use `unknown` if type truly unknown
- **Define interfaces** before implementing
- **Use strict null checks** - handle undefined explicitly
- **Prefer type inference** over explicit types where clear

### React
- **Functional components** only (no classes)
- **Custom hooks** for reusable logic
- **useCallback** for functions passed as props
- **useMemo** for expensive calculations
- **Proper dependency arrays** in useEffect/useMemo/useCallback

### Styling
- **Tailwind utilities** over custom CSS
- **Mobile-first** responsive design
- **Semantic HTML** (nav, main, section, article)
- **Accessible** (aria-labels, keyboard navigation)

---

## Key Files Reference

| File | Purpose | When to Edit |
|------|---------|--------------|
| `src/App.tsx` | Root component, routing | Adding routes, global state |
| `src/contexts/AuthContext.tsx` | Authentication state | Changing auth flow |
| `src/contexts/GradingContext.tsx` | Grading workflow state | Adding form fields, validation |
| `src/services/api.ts` | Backend API client | New endpoints, error handling |
| `src/types/api.ts` | Backend type definitions | API contract changes |
| `src/components/input/EssayTypeSelector.tsx` | Essay type picker | Adding new essay types |
| `src/components/ui/ResultsDisplay.tsx` | Grading results UI | Changing results layout |
| `build.js` | ESBuild configuration | Build optimization, plugins |
| `vercel.json` | Vercel deployment config | Deployment settings |

---

## Quick Reference

**Start dev server:**
```bash
npm run dev
# http://127.0.0.1:8001
```

**Build for production:**
```bash
npm run build
# Output: /dist
```

**Rebuild CSS:**
```bash
npm run build:css
```

**Type checking:**
```bash
npx tsc --noEmit
```

**Production URL:**
https://apushgrader.vercel.app

**Backend API:**
https://apush-grader-production.up.railway.app
