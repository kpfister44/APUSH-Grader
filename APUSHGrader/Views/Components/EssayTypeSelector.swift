import SwiftUI

struct EssayTypeSelector: View {
    @Binding var selectedType: EssayType
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Essay Type")
                .font(.headline)
            
            Picker("Essay Type", selection: $selectedType) {
                ForEach(EssayType.allCases, id: \.self) { type in
                    Text(type.rawValue).tag(type)
                }
            }
            .pickerStyle(SegmentedPickerStyle())
            
            Text(selectedType.description)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding(.horizontal)
    }
}

#Preview {
    EssayTypeSelector(selectedType: .constant(.dbq))
}