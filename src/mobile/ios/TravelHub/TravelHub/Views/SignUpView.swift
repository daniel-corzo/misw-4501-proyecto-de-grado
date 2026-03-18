//
//  SignUpView.swift
//  TravelHub
//
//  Created by Andres Donoso on 17/03/26.
//

import SwiftUI

struct SignUpView: View {
    @State private var fullName: String = ""
    @State private var phone: String = ""
    @State private var email: String = ""
    @State private var password: String = ""

    var rawPhone: String {
        phone.filter { $0.isNumber }
    }

    var body: some View {
        ZStack {
            Color.formBackground
                .ignoresSafeArea()

            VStack(alignment: .leading) {
                Text(LocalizedStringResource.SignUp.title)
                    .font(.title)
                    .bold()

                Text(LocalizedStringResource.SignUp.description)
                    .foregroundStyle(.neutralDark)

                VStack(spacing: 32) {

                    // FullName
                    FormTextFieldView(
                        fieldName: .UserData.fullName,
                        icon: "person",
                        placeholder: "John Doe",
                        textInputAutocapitalization: .words,
                        text: $fullName
                    )
                    .textContentType(.name)

                    //Phone Number
                    FormTextFieldView(
                        fieldName: .UserData.phone,
                        icon: "phone",
                        placeholder: "3214567890",
                        text: $phone
                    )
                    .keyboardType(.phonePad)
                    .onChange(of: phone) { _, newValue in
                        phone = formatPhone(newValue)
                    }
                    .textContentType(.telephoneNumber)

                    // Email
                    FormTextFieldView(
                        fieldName: .UserData.email,
                        icon: "envelope",
                        placeholder: "example@mail.com",
                        text: $email
                    )
                    .keyboardType(.emailAddress)
                    .textContentType(.emailAddress)

                    // Password
                    FormTextFieldView(
                        fieldName: .UserData.password,
                        icon: "lock",
                        placeholder: LocalizedStringResource.SignUp
                            .passwordPlaceholder,
                        isSecuredField: true,
                        text: $password
                    )
                    .textContentType(.newPassword)
                }  //: VStack Form
            }  //: VStack
        }  //: ZStack Background
    }
}

#Preview {
    SignUpView()
}
