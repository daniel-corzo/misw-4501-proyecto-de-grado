//
//  CapsuleTextField.swift
//  TravelHub
//
//  Created by Andres Donoso on 17/03/26.
//

import SwiftUI

struct CapsuleTextField: View {
    let icon: String
    let placeholder: String
    let textInputAutocapitalization: TextInputAutocapitalization?
    
    @Binding var text: String
    
    init(icon: String,
         placeholder: String,
         textInputAutocapitalization: TextInputAutocapitalization? = nil,
         text: Binding<String>) {
        self.icon = icon
        self.placeholder = placeholder
        self.textInputAutocapitalization = textInputAutocapitalization
        self._text = text
    }
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(.gray)
            TextField(placeholder, text: $text)
                .textInputAutocapitalization(textInputAutocapitalization)
        }
        .padding()
        .background(Color.white)
        .clipShape(.capsule)
        .overlay(
            Capsule()
                .stroke(Color.gray.opacity(0.4), lineWidth: 1)
        )
    }
}

#Preview {
    @Previewable @State var fullName: String = ""
    
    CapsuleTextField(icon: "person", placeholder: "John Doe", textInputAutocapitalization: .words, text: $fullName)
}
