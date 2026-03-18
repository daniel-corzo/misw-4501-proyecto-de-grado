//
//  CapsuleTextField.swift
//  TravelHub
//
//  Created by Andres Donoso on 17/03/26.
//

import SwiftUI

struct CapsuleTextField: View {
    let icon: String
    let placeholder: LocalizedStringResource
    let textInputAutocapitalization: TextInputAutocapitalization?
    let isSecuredField: Bool

    @Binding var text: String

    init(
        icon: String,
        placeholder: LocalizedStringResource,
        textInputAutocapitalization: TextInputAutocapitalization? = nil,
        isSecuredField: Bool = false,
        text: Binding<String>
    ) {
        self.icon = icon
        self.placeholder = placeholder
        self.textInputAutocapitalization = textInputAutocapitalization
        self.isSecuredField = isSecuredField

        self._text = text
    }

    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(.gray)

            if isSecuredField {
                SecureField(placeholder, text: $text)
            } else {
                TextField(placeholder, text: $text)
                    .textInputAutocapitalization(textInputAutocapitalization)
            }

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
    @Previewable @State var password: String = ""

    CapsuleTextField(
        icon: "person",
        placeholder: "John Doe",
        textInputAutocapitalization: .words,
        text: $fullName
    )

    CapsuleTextField(
        icon: "lock",
        placeholder: "Password",
        isSecuredField: true,
        text: $password
    )
}
