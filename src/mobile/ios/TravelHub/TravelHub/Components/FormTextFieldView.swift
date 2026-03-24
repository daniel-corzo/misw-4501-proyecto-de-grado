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
    let smallText: AttributedString?

    @Binding var text: String

    init(
        fieldName: LocalizedStringResource,
        icon: String,
        placeholder: LocalizedStringResource,
        textInputAutocapitalization: TextInputAutocapitalization? = nil,
        isSecuredField: Bool = false,
        smallText: AttributedString? = nil,
        text: Binding<String>
    ) {
        self.fieldName = fieldName
        self.icon = icon
        self.placeholder = placeholder
        self.textInputAutocapitalization = textInputAutocapitalization
        self.isSecuredField = isSecuredField
        self.smallText = smallText

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
            
            if let smallText {
                Text(smallText)
            }
        }
    }
}

#Preview(traits: .sizeThatFitsLayout) {
    @Previewable @State var fullName: String = ""
    
    var smallText: AttributedString {
        var someGreenText: AttributedString = "Some green text"
        someGreenText.foregroundColor = .success
        
        var someRedText: AttributedString = "Some red text"
        someRedText.foregroundColor = .danger
        
        var someNeutralText: AttributedString = "Some neutral text"
        someNeutralText.foregroundColor = .neutralDark
        
        return someGreenText + "\n" + someRedText + "\n" + someNeutralText
    }

    FormTextFieldView(
        fieldName: .UserData.fullName,
        icon: "person",
        placeholder: "John Doe",
        textInputAutocapitalization: .words,
        smallText: smallText,
        text: $fullName
    )
    .padding()
}
