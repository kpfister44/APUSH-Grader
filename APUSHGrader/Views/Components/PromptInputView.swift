import SwiftUI

struct PromptInputView: View {
    @Binding var text: String
    let essayType: EssayType
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Prompt/Question")
                .font(.headline)
            
            ZStack(alignment: .topLeading) {
                TextEditor(text: $text)
                    .padding(8)
                    .background(Color(.systemGray6))
                    .cornerRadius(8)
                    .frame(minHeight: 80)
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color(.systemGray4), lineWidth: 1)
                    )
                
                if text.isEmpty {
                    Text(essayType.promptPlaceholderText)
                        .foregroundColor(.secondary)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 16)
                        .allowsHitTesting(false)
                }
            }
        }
        .padding(.horizontal)
    }
}

#Preview {
    PromptInputView(text: .constant(""), essayType: .dbq)
}