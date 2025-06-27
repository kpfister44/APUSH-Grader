import SwiftUI
import APUSHGraderCore

struct GradeButton: View {
    let essayType: EssayType
    let isGrading: Bool
    let isEnabled: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack {
                if isGrading {
                    ProgressView()
                        .scaleEffect(0.8)
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                }
                Text(isGrading ? "Grading..." : "Grade \(essayType.rawValue)")
            }
            .foregroundColor(.white)
            .padding()
            .frame(maxWidth: .infinity)
            .background(isEnabled ? Color.blue : Color.gray)
            .cornerRadius(10)
        }
        .disabled(!isEnabled || isGrading)
        .padding(.horizontal)
    }
}

#Preview {
    VStack(spacing: 20) {
        GradeButton(
            essayType: .dbq,
            isGrading: false,
            isEnabled: true,
            action: {}
        )
        
        GradeButton(
            essayType: .leq,
            isGrading: true,
            isEnabled: true,
            action: {}
        )
        
        GradeButton(
            essayType: .saq,
            isGrading: false,
            isEnabled: false,
            action: {}
        )
    }
    .padding()
}