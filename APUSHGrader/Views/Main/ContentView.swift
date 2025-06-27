import SwiftUI

struct ContentView: View {
    @State private var essayText: String = ""
    @State private var promptText: String = ""
    @State private var isGrading = false
    @State private var gradeResult: String = ""
    @State private var essayType: EssayType = .dbq
    @State private var processedResult: ProcessedGradingResult?
    @State private var errorMessage: String?
    @State private var showingErrorAlert = false
    
    private let apiService: APIServiceProtocol = //APIService()
        MockAPIService()
    // Use MockAPIService() for testing without API calls
    
    private var isFormValid: Bool {
        !essayText.isEmpty && !promptText.isEmpty
    }
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    HeaderView()
                    
                    EssayTypeSelector(selectedType: $essayType)
                    
                    PromptInputView(text: $promptText, essayType: essayType)
                    
                    EssayInputView(text: $essayText, essayType: essayType)
                    
                    GradeButton(
                        essayType: essayType,
                        isGrading: isGrading,
                        isEnabled: isFormValid,
                        action: gradeEssay
                    )
                    
                    if let processedResult = processedResult {
                        GradeResultsView(result: processedResult)
                            .transition(.opacity.combined(with: .scale))
                    }
                    
                    // Bottom padding for scroll view
                    Color.clear.frame(height: 20)
                }
                .padding(.bottom, 20)
            }
        }
        .alert("Grading Error", isPresented: $showingErrorAlert) {
            Button("OK") { }
        } message: {
            Text(errorMessage ?? "An unknown error occurred")
        }
    }
    
    private func gradeEssay() {
        isGrading = true
        processedResult = nil
        errorMessage = nil
        
        Task {
            do {
                // Call the API service
                let response = try await apiService.gradeEssay(essayText, type: essayType, prompt: promptText)
                
                // Process the response
                let processed = ResponseProcessor.processGradingResponse(response, for: essayType)
                
                await MainActor.run {
                    withAnimation(.easeInOut(duration: 0.5)) {
                        self.processedResult = processed
                        self.gradeResult = processed.formattedText
                    }
                    self.isGrading = false
                }
                
            } catch {
                await MainActor.run {
                    self.errorMessage = ErrorPresentation.getUserFriendlyMessage(for: error)
                    self.showingErrorAlert = true
                    self.isGrading = false
                }
            }
        }
    }
}

// MARK: - Header Component

private struct HeaderView: View {
    var body: some View {
        VStack(spacing: 8) {
            Text("APUSH Essay Grader")
                .font(.largeTitle)
                .fontWeight(.bold)
                .padding(.top, 10)
            
            Text("Select essay type and enter your response to get it graded using College Board rubrics")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
        }
    }
}

#Preview {
    ContentView()
}