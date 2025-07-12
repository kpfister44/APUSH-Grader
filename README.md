# APUSH Grader

A modern AI-powered essay grading system for AP US History, featuring a **Python FastAPI backend** with **iOS SwiftUI frontend**. Uses Anthropic Claude 3.5 Sonnet to grade essays based on official College Board rubrics.

## 🏗️ Architecture

**Current Architecture (Phase 3 Complete):**
```
iOS App (SwiftUI) → HTTP API → Python Backend (FastAPI) → Anthropic Claude 3.5 Sonnet
```

- **iOS Frontend**: Clean SwiftUI interface for essay input and results display
- **Python Backend**: Production-ready FastAPI service with comprehensive business logic
- **AI Integration**: Real Anthropic Claude 3.5 Sonnet API for accurate essay grading
- **Production Features**: Rate limiting, structured logging, usage safeguards, health monitoring

## ✨ Features

### Essay Grading
- **Multiple Essay Types**: DBQ (6 pts), LEQ (6 pts), SAQ (3 pts)
- **College Board Rubrics**: Official AP US History scoring guidelines
- **Detailed Feedback**: Comprehensive breakdown by rubric sections
- **Performance Analysis**: Strengths, improvements, and strategic tips
- **Real-time Grading**: Powered by Anthropic Claude 3.5 Sonnet

### User Experience
- **Clean SwiftUI Interface**: Optimized for iPhone and iPad
- **Responsive Design**: Works seamlessly across all iOS devices
- **Loading States**: Visual feedback during grading process
- **Error Handling**: User-friendly messages for network issues
- **SwiftUI Previews**: Real-time testing with actual backend

### Production Ready
- **Rate Limiting**: 20 requests/minute, 50 essays/hour
- **Usage Safeguards**: 100 essays/day, 50,000 words/day limits
- **Cost Protection**: Daily limits prevent excessive API usage
- **Structured Logging**: JSON logs with correlation IDs
- **Health Monitoring**: `/health` and `/usage/summary` endpoints

## 🚀 Quick Start

### Prerequisites
- **iOS Development**: Xcode 15.0+, iOS 17.0+, Swift 5.0+
- **Python Backend**: Python 3.10+, FastAPI, Anthropic API key
- **Target Audience**: 2-12 teachers (hobby project scale)

### 1. Setup Python Backend

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configure environment (create .env file)
echo "AI_SERVICE_TYPE=anthropic" > .env
echo "ANTHROPIC_API_KEY=your-api-key-here" >> .env

# Run the server
uvicorn app.main:app --reload
```

### 2. Setup iOS App

```bash
# Open Xcode project
open APUSHGrader.xcodeproj

# Build and run in Xcode (⌘+R)
# Ensure backend is running on localhost:8000
```

### 3. Test Integration

1. **Start Python backend** (see step 1)
2. **Open iOS app** in Xcode or simulator
3. **Enter test essay** and prompt
4. **Tap "Grade Essay"** to test end-to-end integration
5. **View results** with real AI feedback

## 📊 API Documentation

### REST Endpoints

**Grade Essay:**
```http
POST http://localhost:8000/api/v1/grade
Content-Type: application/json

{
  "essay_text": "Your essay content here...",
  "essay_type": "DBQ",
  "prompt": "Essay question/prompt"
}
```

**Health Check:**
```http
GET http://localhost:8000/health
GET http://localhost:8000/health/detailed
GET http://localhost:8000/usage/summary
```

**Interactive Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Testing

### Python Backend
```bash
cd backend
source venv/bin/activate

# Run all tests (320+ comprehensive tests)
pytest tests/ -v

# Run specific test suites
pytest tests/integration/ -v           # End-to-end tests
pytest tests/services/processing/ -v   # Processing services
pytest tests/services/ai/ -v           # AI integration tests
```

### iOS App
- **Xcode Testing**: ⌘+U for unit tests
- **SwiftUI Previews**: Real-time testing with actual backend
- **Manual Testing**: Build and run in simulator

## 🌐 Deployment

### Development (Local)
- **Backend**: `uvicorn app.main:app --reload`
- **Frontend**: Xcode build and run
- **API Base URL**: `http://localhost:8000`

### Production Options
- **Railway**: Recommended ($5-10/month)
- **Heroku**: Alternative cloud hosting
- **Docker**: Container deployment
- **Self-hosted**: VPS with PM2/systemd

See [backend/README.md](backend/README.md) for detailed deployment guides.

## 💰 Cost Management

### Anthropic API Costs
- **Input tokens**: ~$3.00 per 1M tokens
- **Output tokens**: ~$15.00 per 1M tokens  
- **Typical essay**: ~$0.02-0.03 per grading

### Built-in Protections
- **Daily limits**: 100 essays/day, 50k words/day
- **Rate limiting**: 20 requests/minute
- **Usage tracking**: Real-time monitoring
- **Teacher budgets**: ~$10-30/month for typical usage

See [backend/COST_GUIDE.md](backend/COST_GUIDE.md) for detailed cost analysis.

## 📁 Project Structure

```
APUSH-Grader/
├── APUSHGrader/                 # iOS SwiftUI App
│   ├── Models/                  # API response DTOs
│   ├── Services/                # NetworkService for HTTP
│   ├── Views/                   # SwiftUI interface
│   └── Resources/               # Assets and configs
├── backend/                     # Python FastAPI Backend
│   ├── app/                     # Application code
│   │   ├── api/routes/          # REST endpoints
│   │   ├── models/              # Pydantic data models
│   │   ├── services/            # Business logic
│   │   └── middleware/          # Production middleware
│   ├── tests/                   # 320+ comprehensive tests
│   ├── requirements.txt         # Dependencies
│   └── .env                     # Environment config
├── CLAUDE.md                    # AI development guidance
├── PLAN.md                      # Migration timeline
└── README.md                    # This file
```

## 🛠️ Development

### AI Service Configuration
```bash
# Mock AI (no API key required)
AI_SERVICE_TYPE=mock

# Real Anthropic AI (requires API key)
AI_SERVICE_TYPE=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

### Common Commands
```bash
# Backend development
cd backend && source venv/bin/activate
uvicorn app.main:app --reload        # Start server
pytest tests/ -v                     # Run tests

# iOS development  
open APUSHGrader.xcodeproj           # Open in Xcode
# ⌘+B to build, ⌘+R to run
```

## 📈 Migration History

✅ **Phase 1**: Python FastAPI backend foundation  
✅ **Phase 2**: Production readiness + real AI integration  
✅ **Phase 3**: iOS frontend migration to API (APUSHGraderCore removed)  
🔄 **Phase 4**: Production deployment (in progress)

**Key Achievement**: Successfully migrated from monolithic iOS app to clean client-server architecture, removing 3,146 lines of complex Swift business logic while preserving excellent UI.

## 🎯 Target Audience

Designed for **2-12 AP US History teachers** who need:
- Quick, accurate essay grading
- College Board rubric compliance  
- Simple setup and maintenance
- Cost-effective AI integration
- Professional feedback generation

## 📄 License

This project is for educational purposes.

## 🤝 Contributing

This is a hobby project focused on simplicity. The codebase prioritizes functionality over enterprise features.

---

**Ready to grade APUSH essays with AI?** 🚀  
Start with the [Quick Start](#-quick-start) guide above!