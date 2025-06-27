# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
APUSH Grader - iOS SwiftUI app that uses AI (OpenAI/Anthropic) to grade AP US History essays based on College Board rubrics.

## Repository Architecture - Hybrid SPM/iOS Structure
The project uses a **hybrid architecture** with business logic in a Swift Package and UI in the iOS app:

### **APUSHGraderCore/** - Swift Package (Business Logic)
- **Package.swift** - SPM configuration for iOS 16+, includes test targets
- **Sources/APUSHGraderCore/**
  - **Models/Core/** - Core data models (all public)
    - **EssayType.swift** - Essay type enum with UI properties and scoring rules
    - **GradeModels.swift** - Core grading structures (GradeResponse, RubricItem, etc.)
    - **APIModels.swift** - API configuration and model definitions
  - **Models/Processing/** - Processing data models  
    - **PreprocessingModels.swift** - Text processing result structures
  - **Services/API/** - API service implementations (all public)
    - **APIServiceProtocol.swift** - Service interface definitions
    - **APIService.swift** - Main coordinator with retry logic
    - **OpenAIService.swift** - OpenAI-specific implementation
    - **AnthropicService.swift** - Anthropic-specific implementation  
    - **MockAPIService.swift** - Testing implementation
  - **Services/Processing/** - Business logic processing (all public)
    - **EssayProcessing/** - Text preprocessing and validation
    - **ResponseProcessing/** - AI response processing  
    - **PromptGeneration/** - AI prompt generation
- **Tests/APUSHGraderCoreTests/** - Unit tests for business logic

### **APUSHGrader/** - iOS App (UI Layer)
- **Views/** - SwiftUI views (import APUSHGraderCore)
  - **Main/ContentView.swift** - Main app coordinator
  - **Main/GradeResultsView.swift** - Detailed results display
  - **Components/** - Reusable UI components
- **App/** - Application configuration
  - **APUSHGraderApp.swift** - App entry point (cleaned up)
  - **Info.plist** - API keys and app configuration
- **Resources/** - Assets and preview content
- **Utilities/** - Empty directories for future extensions/helpers

## Development Commands
- **iOS App**: ⌘+B in Xcode, ⌘+R to run, Product → Clean Build Folder
- **Swift Package Testing**: `cd APUSHGraderCore && swift test` (command line)
- **Swift Package Build**: `cd APUSHGraderCore && swift build` (command line)

## Testing

### **Current Testing Status** 
✅ **Hybrid SPM/iOS architecture implemented** - Business logic extracted to Swift Package
✅ **Core business logic validated** with simple tests (ready for comprehensive SPM testing)
✅ **Swift Package builds successfully** with command line testing capability
✅ **iOS app builds and previews work** - UI layer properly imports APUSHGraderCore
📋 **Ready for Step 3**: Comprehensive SPM test suite development

### **Completed Steps**
**Step 1**: ✅ Created Swift Package structure for APUSHGraderCore
**Step 2**: ✅ Moved Models/ and Services/ to Swift Package, updated iOS app integration
**Step 3**: 📋 **NEXT SESSION** - Create comprehensive test suite using `swift test`

### **Testing Plan - Step 3: Comprehensive SPM Test Suite (NEXT PRIORITY)**
1. **Core Model Testing** - Test `EssayType`, `GradeModels`, scoring calculations
2. **API Service Testing** - Test `APIService`, `MockAPIService`, retry logic, error handling  
3. **Essay Processing Testing** - Test `EssayProcessor`, validation, text analysis
4. **Response Processing Testing** - Test `ResponseProcessor`, `ResponseValidator`, `InsightsGenerator`
5. **Prompt Generation Testing** - Test `PromptGenerator` for DBQ/LEQ/SAQ specific prompts
6. **Integration Testing** - End-to-end testing of business logic workflows

### **Already Validated Business Logic**
- ✅ **Core scoring calculations** - Percentage/letter grade math, performance levels
- ✅ **Essay validation** - Word count limits, length checking for DBQ/LEQ/SAQ
- ✅ **Text analysis** - Word/paragraph counting, thesis/evidence detection
- ✅ **Essay type-specific rules** - Different requirements for each essay type

### **Test Configuration**
- **Swift Package Tests**: Run `cd APUSHGraderCore && swift test`
- **Mock API**: Use `MockAPIService()` in Views/Main/ContentView.swift line 13-14
- **Real AI**: Use `APIService()` in Views/Main/ContentView.swift line 13-14  
- **API Keys**: Stored in App/Info.plist (OPENAI_API_KEY, ANTHROPIC_API_KEY)
- **UI Testing**: SwiftUI previews work for all components

## Essay Types Supported
- **DBQ** (Document-Based Question) - 6 points
- **LEQ** (Long Essay Question) - 6 points  
- **SAQ** (Short Answer Question) - 3 points

## Current Status
✅ **Hybrid SPM/iOS architecture successfully implemented**
✅ **Business logic extracted to Swift Package** - APUSHGraderCore with public APIs
✅ **iOS app builds and runs** - Proper import of APUSHGraderCore 
✅ **SwiftUI previews working** - UI development capabilities preserved
✅ **Command line testing ready** - Can run `swift test` in APUSHGraderCore/
✅ Fully functional with mock API
✅ Real API keys configured in Info.plist
✅ Prompt input feature - users can enter the specific question/prompt
✅ UI flow: Essay Type → Prompt Input → Essay Text → Grade Button
✅ **Core business logic validated** through simple testing
⚠️ **NOT YET TESTED** with actual AI APIs (OpenAI/Anthropic)
✅ Scrollable UI with detailed breakdown
📋 **Next session priority**: Create comprehensive SPM test suite (Step 3)
📋 Ready for real API testing - just switch to `APIService()` in ContentView.swift

## Architecture Benefits
- **Hybrid Structure**: Best of both worlds - SPM testing + iOS capabilities
- **Clean Module Boundaries**: Business logic separate from UI layer
- **Command Line Testing**: Can run `swift test` for rapid iteration
- **iOS Development Preserved**: Xcode previews, App Store deployment, Info.plist
- **Public API Design**: Forced clean interfaces between modules
- **Single Responsibility**: Each file has one clear purpose  
- **Testability**: Business logic can be unit tested independently
- **Maintainability**: Easy to find and modify specific functionality
- **Reusability**: UI components can be used across different views
- **Scalability**: Easy to add new features without affecting existing code

## Common Issues
- **SPM Access Control**: All types used by iOS app must be `public` in APUSHGraderCore
- **Missing Initializers**: Add `public init(...)` for structs used in iOS app
- Multi-line strings must start content on new line after `"""`
- Info.plist conflicts: Use `GENERATE_INFOPLIST_FILE = NO`
- Unicode characters in strings: Use escape sequences like `\u{201C}`
- When adding new UI components, place them in APUSHGrader/Views/Components/
- When adding new business logic, place them in APUSHGraderCore/Sources/APUSHGraderCore/
