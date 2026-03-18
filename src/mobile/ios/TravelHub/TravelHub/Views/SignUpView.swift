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

    @State private var agreeToTerms: Bool = false

    var rawPhone: String {
        phone.filter { $0.isNumber }
    }

    var agreementText: AttributedString {
        var text = AttributedString(
            "I agree to the Terms of Service and Privacy Policy"
        )

        if let termsRange = text.range(of: "Terms of Service") {
            text[termsRange].foregroundColor = .blue
        }

        if let privacyRange = text.range(of: "Privacy Policy") {
            text[privacyRange].foregroundColor = .blue
        }

        return text
    }

    var body: some View {
        ZStack {
            Color.formBackground
                .ignoresSafeArea()

            ScrollView(.vertical) {
                VStack(alignment: .leading, spacing: 32) {
                    VStack(alignment: .leading) {
                        Text(LocalizedStringResource.SignUp.title)
                            .font(.title)
                            .bold()
                        
                        Text(LocalizedStringResource.SignUp.description)
                            .foregroundStyle(.neutralDark)
                    }
                    
                    VStack(spacing: 24) {
                        
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
                        
                        HStack {
                            Button {
                                agreeToTerms.toggle()
                            } label: {
                                Image(
                                    systemName: agreeToTerms
                                    ? "checkmark.square.fill" : "square"
                                )
                                .foregroundStyle(agreeToTerms ? .accent : .gray)
                                .font(.system(size: 30))
                            }  //: Button Label
                            
                            Text(agreementText)
                                .foregroundStyle(.primary)
                                .multilineTextAlignment(.leading)
                                .fixedSize(horizontal: false, vertical: true)
                        }  //: HStack Terms
                        .frame(maxWidth: .infinity, alignment: .leading)
                    }  //: VStack Form
                    
                    Button {
                        // TODO: Implement this
                    } label: {
                        HStack {
                            Spacer()
                            
                            Text(LocalizedStringResource.SignUp.createAccountButton)
                                .foregroundStyle(.white)
                                .bold()
                            
                            Image(systemName: "arrow.right")
                                .foregroundStyle(.white)
                                .bold()
                            
                            Spacer()
                        }
                    }
                    .padding(.vertical, 24)
                    .glassEffect(.regular.tint(.accent).interactive())
                    .clipShape(.capsule)
                    .shadow(color: .accent.opacity(0.2), radius: 15, y: 10)
                    .glassEffect()
                    
                    Divider()
                    
                    HStack {
                        Spacer()
                        
                        Text(LocalizedStringResource.SignUp.alreadyHaveAccount)
                        
                        // TODO: Change this to navigation link when login exists
                        Text(LocalizedStringResource.SignUp.loginText)
                            .bold()
                            .foregroundStyle(.accent)
                        
                        Spacer()
                    }
                    
                }  //: VStack Container
                .padding()
            } //: ScrollView
            .scrollDismissesKeyboard(.immediately)
        }  //: ZStack Background
        .onTapGesture {
            UIApplication.shared.sendAction(
                #selector(UIResponder.resignFirstResponder),
                to: nil, from: nil, for: nil
            )
        }
    }
}

#Preview {
    SignUpView()
}
