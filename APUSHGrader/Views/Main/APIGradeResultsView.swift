import SwiftUI

struct APIGradeResultsView: View {
    let result: APIProcessedGradingResult
    @State private var showingDetailedBreakdown = false
    
    var body: some View {
        VStack(spacing: 16) {
            // Score header
            APIScoreHeaderView(displayData: result.displayData)
            
            // Quick insights
            if !result.insights.isEmpty {
                APIInsightsView(insights: result.insights)
            }
            
            // Validation issues warning
            if !result.validationIssues.isEmpty {
                APIValidationIssuesView(issues: result.validationIssues)
            }
            
            // Breakdown toggle
            Button(action: {
                withAnimation(.easeInOut) {
                    showingDetailedBreakdown.toggle()
                }
            }) {
                HStack {
                    Text(showingDetailedBreakdown ? "Hide Details" : "Show Detailed Breakdown")
                        .fontWeight(.medium)
                    Image(systemName: showingDetailedBreakdown ? "chevron.up" : "chevron.down")
                }
                .foregroundColor(.blue)
            }
            
            // Detailed breakdown
            if showingDetailedBreakdown {
                APIDetailedBreakdownView(breakdown: result.originalResponse.breakdown)
                    .transition(.opacity.combined(with: .slide))
            }
            
            // Overall feedback
            APIFeedbackView(
                feedback: result.originalResponse.overallFeedback,
                suggestions: result.originalResponse.suggestions
            )
        }
        .padding(.horizontal)
    }
}

// MARK: - Score Header

struct APIScoreHeaderView: View {
    let displayData: APIGradeDisplayData
    
    var body: some View {
        VStack(spacing: 8) {
            HStack {
                Text("Grade")
                    .font(.headline)
                    .foregroundColor(.secondary)
                Spacer()
            }
            
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(displayData.scoreText)
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .foregroundColor(displayData.performanceColor)
                    
                    HStack(spacing: 12) {
                        Text(displayData.percentageText)
                            .font(.title2)
                            .fontWeight(.semibold)
                            .foregroundColor(displayData.performanceColor)
                        
                        Text(displayData.letterGrade)
                            .font(.title2)
                            .fontWeight(.semibold)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(displayData.performanceColor.opacity(0.1))
                            .foregroundColor(displayData.performanceColor)
                            .cornerRadius(6)
                    }
                }
                
                Spacer()
                
                // Performance indicator
                APICircularProgressView(
                    percentage: Double(displayData.percentageText.dropLast()) ?? 0,
                    color: displayData.performanceColor
                )
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
}

// MARK: - Circular Progress View

struct APICircularProgressView: View {
    let percentage: Double
    let color: Color
    
    var body: some View {
        ZStack {
            Circle()
                .stroke(color.opacity(0.2), lineWidth: 8)
                .frame(width: 60, height: 60)
            
            Circle()
                .trim(from: 0, to: percentage / 100)
                .stroke(color, style: StrokeStyle(lineWidth: 8, lineCap: .round))
                .frame(width: 60, height: 60)
                .rotationEffect(.degrees(-90))
                .animation(.easeInOut(duration: 1), value: percentage)
            
            Text("\(Int(percentage))%")
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundColor(color)
        }
    }
}

// MARK: - Insights View

struct APIInsightsView: View {
    let insights: [APIGradingInsight]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Key Insights")
                .font(.headline)
            
            ForEach(Array(insights.enumerated()), id: \.offset) { index, insight in
                APIInsightRowView(insight: insight)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color(.systemGray4), lineWidth: 1)
        )
    }
}

struct APIInsightRowView: View {
    let insight: APIGradingInsight
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: iconForInsightType(insight.type))
                .foregroundColor(colorForSeverity(insight.severity))
                .frame(width: 16)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(insight.title)
                    .font(.subheadline)
                    .fontWeight(.semibold)
                
                Text(insight.message)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.leading)
            }
            
            Spacer()
        }
        .padding(.vertical, 4)
    }
    
    private func iconForInsightType(_ type: APIInsightType) -> String {
        switch type {
        case .performance: return "chart.bar.fill"
        case .strength: return "checkmark.circle.fill"
        case .improvement: return "arrow.up.circle.fill"
        case .tip: return "lightbulb.fill"
        case .warning: return "exclamationmark.triangle.fill"
        }
    }
    
    private func colorForSeverity(_ severity: APIInsightSeverity) -> Color {
        switch severity {
        case .info: return .blue
        case .warning: return .orange
        case .error: return .red
        case .success: return .green
        }
    }
}

// MARK: - Validation Issues View

struct APIValidationIssuesView: View {
    let issues: [String]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: "exclamationmark.triangle.fill")
                    .foregroundColor(.orange)
                Text("Validation Issues")
                    .font(.headline)
                    .foregroundColor(.orange)
            }
            
            ForEach(issues, id: \.self) { issue in
                HStack(alignment: .top) {
                    Text("•")
                        .foregroundColor(.orange)
                    Text(issue)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding()
        .background(Color.orange.opacity(0.1))
        .cornerRadius(12)
    }
}

// MARK: - Detailed Breakdown View

struct APIDetailedBreakdownView: View {
    let breakdown: [String: APIRubricItem]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Detailed Rubric Breakdown")
                .font(.headline)
            
            VStack(spacing: 8) {
                ForEach(breakdown.keys.sorted(), id: \.self) { key in
                    if let item = breakdown[key] {
                        APIRubricItemView(item: item, name: key.capitalized)
                    }
                }
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
}

struct APIRubricItemView: View {
    let item: APIRubricItem
    let name: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text(name)
                    .font(.subheadline)
                    .fontWeight(.semibold)
                
                Spacer()
                
                Text("\(item.score)/\(item.maxScore)")
                    .font(.subheadline)
                    .fontWeight(.bold)
                    .foregroundColor(item.isFullCredit ? .green : (item.score > 0 ? .orange : .red))
                
                Image(systemName: item.isFullCredit ? "checkmark.circle.fill" : (item.score > 0 ? "minus.circle.fill" : "xmark.circle.fill"))
                    .foregroundColor(item.isFullCredit ? .green : (item.score > 0 ? .orange : .red))
            }
            
            Text(item.feedback)
                .font(.caption)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.leading)
            
            // Progress bar
            ProgressView(value: Double(item.score), total: Double(item.maxScore))
                .progressViewStyle(LinearProgressViewStyle(tint: item.isFullCredit ? .green : (item.score > 0 ? .orange : .red)))
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(8)
    }
}

// MARK: - Feedback View

struct APIFeedbackView: View {
    let feedback: String
    let suggestions: [String]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Overall feedback
            VStack(alignment: .leading, spacing: 8) {
                Text("Overall Feedback")
                    .font(.headline)
                
                Text(feedback)
                    .font(.body)
                    .foregroundColor(.primary)
                    .multilineTextAlignment(.leading)
            }
            
            // Suggestions
            if !suggestions.isEmpty {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Suggestions for Improvement")
                        .font(.headline)
                    
                    ForEach(Array(suggestions.enumerated()), id: \.offset) { index, suggestion in
                        HStack(alignment: .top, spacing: 8) {
                            Text("\(index + 1).")
                                .font(.body)
                                .fontWeight(.semibold)
                                .foregroundColor(.blue)
                            
                            Text(suggestion)
                                .font(.body)
                                .multilineTextAlignment(.leading)
                        }
                    }
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color(.systemGray4), lineWidth: 1)
        )
    }
}

// MARK: - Preview

#Preview {
    let mockGradingResponse = GradingResponse(
        score: 4,
        maxScore: 6,
        percentage: 67.0,
        letterGrade: "C+",
        performanceLevel: "Developing",
        breakdown: [
            "thesis": RubricItemResponse(score: 1, maxScore: 1, feedback: "Clear and defensible thesis"),
            "contextualization": RubricItemResponse(score: 1, maxScore: 1, feedback: "Good historical context"),
            "evidence": RubricItemResponse(score: 1, maxScore: 2, feedback: "Uses some evidence"),
            "analysis": RubricItemResponse(score: 1, maxScore: 2, feedback: "Shows analysis")
        ],
        overallFeedback: "Good essay with room for improvement",
        suggestions: ["Add more evidence", "Improve analysis"],
        warnings: [],
        wordCount: 487,
        paragraphCount: 4,
        processingTimeMs: 1250
    )
    
    let apiResult = APIGradingResult(from: mockGradingResponse)
    let processedResult = APIProcessedGradingResult(from: apiResult)
    
    return ScrollView {
        APIGradeResultsView(result: processedResult)
    }
}