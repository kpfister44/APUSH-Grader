import SwiftUI

struct ContentView: View {
    @State private var essayText: String = ""
    @State private var promptText: String = ""
    @State private var isGrading = false
    @State private var gradeResult: String = ""
    @State private var essayType: EssayType = .dbq
    @State private var processedResult: APIProcessedGradingResult?
    @State private var errorMessage: String?
    @State private var showingErrorAlert = false
    
    // SAQ multi-part fields
    @State private var saqPartA: String = ""
    @State private var saqPartB: String = ""
    @State private var saqPartC: String = ""
    
    private let networkService = NetworkService.shared
    
    private var isFormValid: Bool {
        if essayType == .saq {
            return !promptText.isEmpty && !saqPartA.isEmpty && !saqPartB.isEmpty && !saqPartC.isEmpty
        } else {
            return !essayText.isEmpty && !promptText.isEmpty
        }
    }
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    HeaderView()
                    
                    EssayTypeSelector(selectedType: $essayType)
                        .onChange(of: essayType) { _, _ in
                            clearFields()
                        }
                    
                    PromptInputView(text: $promptText, essayType: essayType)
                    
                    if essayType == .saq {
                        SAQMultiPartInputView(
                            partA: $saqPartA,
                            partB: $saqPartB,
                            partC: $saqPartC
                        )
                    } else {
                        EssayInputView(text: $essayText, essayType: essayType)
                    }
                    
                    GradeButton(
                        essayType: essayType,
                        isGrading: isGrading,
                        isEnabled: isFormValid,
                        action: gradeEssay
                    )
                    
                    if let processedResult = processedResult {
                        APIGradeResultsView(result: processedResult)
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
                // Call the NetworkService with appropriate data based on essay type
                let response: GradingResponse
                
                if essayType == .saq {
                    let saqParts = SAQParts(partA: saqPartA, partB: saqPartB, partC: saqPartC)
                    response = try await networkService.gradeEssayWithSAQParts(
                        saqParts: saqParts,
                        essayType: essayType.rawValue,
                        prompt: promptText
                    )
                } else {
                    response = try await networkService.gradeEssay(
                        essayText: essayText,
                        essayType: essayType.rawValue,
                        prompt: promptText
                    )
                }
                
                // Convert to API models
                let apiResult = APIGradingResult(from: response)
                let processed = APIProcessedGradingResult(from: apiResult)
                
                await MainActor.run {
                    withAnimation(.easeInOut(duration: 0.5)) {
                        self.processedResult = processed
                        self.gradeResult = processed.formattedText
                    }
                    self.isGrading = false
                }
                
            } catch let networkError as NetworkError {
                await MainActor.run {
                    self.errorMessage = networkError.localizedDescription
                    self.showingErrorAlert = true
                    self.isGrading = false
                }
            } catch {
                await MainActor.run {
                    self.errorMessage = "An unexpected error occurred: \(error.localizedDescription)"
                    self.showingErrorAlert = true
                    self.isGrading = false
                }
            }
        }
    }
    
    private func clearFields() {
        // Clear all input fields when essay type changes
        essayText = ""
        saqPartA = ""
        saqPartB = ""
        saqPartC = ""
        promptText = ""
        processedResult = nil
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

// MARK: - SAQ Multi-Part Input Component

private struct SAQMultiPartInputView: View {
    @Binding var partA: String
    @Binding var partB: String
    @Binding var partC: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Image(systemName: "text.book.closed")
                    .foregroundColor(.blue)
                Text("SAQ Response (Three Parts)")
                    .font(.headline)
                    .fontWeight(.medium)
            }
            .padding(.horizontal)
            
            VStack(spacing: 12) {
                // Part A
                VStack(alignment: .leading, spacing: 6) {
                    Label("Part A", systemImage: "a.circle")
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundColor(.blue)
                    
                    TextEditor(text: $partA)
                        .frame(minHeight: 80)
                        .padding(8)
                        .background(Color(.systemGray6))
                        .cornerRadius(8)
                        .overlay(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(Color(.systemGray4), lineWidth: 1)
                        )
                }
                
                // Part B
                VStack(alignment: .leading, spacing: 6) {
                    Label("Part B", systemImage: "b.circle")
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundColor(.blue)
                    
                    TextEditor(text: $partB)
                        .frame(minHeight: 80)
                        .padding(8)
                        .background(Color(.systemGray6))
                        .cornerRadius(8)
                        .overlay(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(Color(.systemGray4), lineWidth: 1)
                        )
                }
                
                // Part C
                VStack(alignment: .leading, spacing: 6) {
                    Label("Part C", systemImage: "c.circle")
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundColor(.blue)
                    
                    TextEditor(text: $partC)
                        .frame(minHeight: 80)
                        .padding(8)
                        .background(Color(.systemGray6))
                        .cornerRadius(8)
                        .overlay(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(Color(.systemGray4), lineWidth: 1)
                        )
                }
            }
            .padding(.horizontal)
        }
        .padding(.vertical, 8)
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 2, x: 0, y: 1)
        .padding(.horizontal)
    }
}

#Preview {
    ContentView()
}