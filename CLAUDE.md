# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
APUSH Grader - iOS SwiftUI app that uses AI (OpenAI/Anthropic) to grade AP US History essays based on College Board rubrics.

## Repository Architecture
The project follows SwiftUI best practices with clear separation of concerns:

### **Models/** 
- **Core/EssayType.swift** - Essay type enum with UI properties and scoring rules
- **Core/GradeModels.swift** - Core grading structures (GradeResponse, RubricItem, etc.)
- **Core/APIModels.swift** - API configuration and model definitions
- **Processing/PreprocessingModels.swift** - Text processing result structures

### **Views/**
- **Main/ContentView.swift** - Main app coordinator (now clean and focused)
- **Main/GradeResultsView.swift** - Detailed results display
- **Components/EssayInputView.swift** - Reusable essay text input
- **Components/PromptInputView.swift** - Reusable prompt input
- **Components/EssayTypeSelector.swift** - Essay type picker component
- **Components/GradeButton.swift** - Grade action button with loading states

### **Services/API/**
- **APIServiceProtocol.swift** - Service interface definitions
- **APIService.swift** - Main coordinator with retry logic
- **OpenAIService.swift** - OpenAI-specific implementation
- **AnthropicService.swift** - Anthropic-specific implementation  
- **MockAPIService.swift** - Testing implementation

### **Services/Processing/**
- **EssayProcessing/** - Text preprocessing and validation
  - **EssayProcessor.swift** - Main coordinator
  - **EssayValidator.swift** - Essay validation logic
  - **TextCleaner.swift** - Text cleaning functions
  - **TextAnalyzer.swift** - Word count, analysis, content checks
  - **WarningGenerator.swift** - Warning generation logic
- **ResponseProcessing/** - AI response processing
  - **ResponseProcessor.swift** - Main coordinator
  - **ResponseValidator.swift** - Response validation
  - **ResponseFormatter.swift** - Display formatting
  - **InsightsGenerator.swift** - Insights and suggestions
  - **ErrorPresentation.swift** - User-friendly error messages
- **PromptGeneration/** - AI prompt generation
  - **PromptGenerator.swift** - System and user prompts for each essay type

### **App/** - Application configuration
- **APUSHGraderApp.swift** - App entry point
- **Info.plist** - API keys and app configuration

### **Resources/** - Assets and preview content
### **Utilities/** - Empty directories for future extensions/helpers

## Development Commands
- Build: ⌘+B in Xcode
- Run: ⌘+R in Xcode
- Clean: Product → Clean Build Folder

## Testing
- **Mock API**: Use `MockAPIService()` in Views/Main/ContentView.swift line 13-14
- **Real AI**: Use `APIService()` in Views/Main/ContentView.swift line 13-14
- **API Keys**: Stored in App/Info.plist (OPENAI_API_KEY, ANTHROPIC_API_KEY)
- **Validation**: Both prompt and essay text must be filled before grading
- **Components**: Each UI component has its own preview for testing

## Essay Types Supported
- **DBQ** (Document-Based Question) - 6 points
- **LEQ** (Long Essay Question) - 6 points  
- **SAQ** (Short Answer Question) - 3 points

## Current Status
✅ Fully reorganized following SwiftUI best practices
✅ Modular UI components with reusable design
✅ Clean separation of concerns across all layers
✅ Fully functional with mock API
✅ Real API keys configured in Info.plist
✅ Prompt input feature - users can enter the specific question/prompt
✅ UI flow: Essay Type → Prompt Input → Essay Text → Grade Button
⚠️ **NOT YET TESTED** with actual AI APIs (OpenAI/Anthropic)
✅ Scrollable UI with detailed breakdown
📋 Ready for real API testing - just switch to `APIService()` in ContentView.swift

## Architecture Benefits
- **Single Responsibility**: Each file has one clear purpose
- **Testability**: Individual components can be unit tested
- **Maintainability**: Easy to find and modify specific functionality
- **Reusability**: UI components can be used across different views
- **Scalability**: Easy to add new features without affecting existing code

## Common Issues
- Multi-line strings must start content on new line after `"""`
- Info.plist conflicts: Use `GENERATE_INFOPLIST_FILE = NO`
- Unicode characters in strings: Use escape sequences like `\u{201C}`
- When adding new UI components, place them in Views/Components/
- When adding new services, follow the existing pattern in Services/