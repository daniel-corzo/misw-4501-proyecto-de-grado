//
//  FormTextFieldView.swift
//  TravelHub
//
//  Created by Andres Donoso on 17/03/26.
//

import SwiftUI

struct FormTextFieldView: View {
    let fieldName: LocalizedStringResource
    let icon: String
    let placeholder: LocalizedStringResource
    let textInputAutocapitalization: TextInputAutocapitalization?
    let isSecuredField: Bool

    @Binding var text: String

    init(
        fieldName: LocalizedStringResource,
        icon: String,
        placeholder: LocalizedStringResource,
        textInputAutocapitalization: TextInputAutocapitalization? = nil,
        isSecuredField: Bool = false,
        text: Binding<String>
    ) {
        self.fieldName = fieldName
        self.icon = icon
        self.placeholder = placeholder
        self.textInputAutocapitalization = textInputAutocapitalization
        self.isSecuredField = isSecuredField

        self._text = text
    }

    var body: some View {
        VStack(alignment: .leading) {
            Text(fieldName)
                .bold()

            CapsuleTextField(
                icon: icon,
                placeholder: placeholder,
                textInputAutocapitalization: textInputAutocapitalization,
                isSecuredField: isSecuredField,
                text: $text
            )
        }
    }
}

#Preview(traits: .sizeThatFitsLayout) {
    @Previewable @State var fullName: String = ""

    FormTextFieldView(
        fieldName: .UserData.fullName,
        icon: "person",
        placeholder: "John Doe",
        textInputAutocapitalization: .words,
        text: $fullName
    )
    .padding()
}
