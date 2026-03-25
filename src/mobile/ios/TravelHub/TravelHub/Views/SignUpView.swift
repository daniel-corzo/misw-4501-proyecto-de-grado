//
//  SignUpView.swift
//  TravelHub
//
//  Created by Andres Donoso on 17/03/26.
//

import SwiftUI

struct SignUpView: View {
    @Environment(\.dismiss) private var dismiss

    @State private var viewModel = ViewModel()

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
                            smallText: viewModel.fullNameSmallText,
                            text: $viewModel.fullName
                        )
                        .textContentType(.name)

                        //Phone Number
                        FormTextFieldView(
                            fieldName: .UserData.phone,
                            icon: "phone",
                            placeholder: "3214567890",
                            smallText: viewModel.phoneSmallText,
                            text: $viewModel.phone
                        )
                        .keyboardType(.phonePad)
                        .onChange(of: viewModel.phone) { _, newValue in
                            viewModel.phone = formatPhone(newValue)
                        }
                        .textContentType(.telephoneNumber)

                        // Email
                        FormTextFieldView(
                            fieldName: .UserData.email,
                            icon: "envelope",
                            placeholder: "example@mail.com",
                            smallText: viewModel.emailSmallText,
                            text: $viewModel.email
                        )
                        .keyboardType(.emailAddress)
                        .textContentType(.emailAddress)

                        // Password
                        FormTextFieldView(
                            fieldName: .UserData.password,
                            icon: "lock",
                            placeholder: LocalizedStringResource.SignUp
                                .passwordPlaceholder,
                            textInputAutocapitalization: .never,
                            isSecuredField: true,
                            smallText: viewModel.passwordSmallText,
                            text: $viewModel.password
                        )
                        .textContentType(.newPassword)

                        HStack {
                            Button {
                                viewModel.agreeToTerms.toggle()
                            } label: {
                                Image(
                                    systemName: viewModel.agreeToTerms
                                        ? "checkmark.square.fill" : "square"
                                )
                                .foregroundStyle(
                                    viewModel.agreeToTerms ? .accent : .gray
                                )
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

                            Text(
                                LocalizedStringResource.SignUp
                                    .createAccountButton
                            )
                            .foregroundStyle(.white)
                            .bold()

                            Image(systemName: "arrow.right")
                                .foregroundStyle(.white)
                                .bold()

                            Spacer()
                        }
                    }
                    .capsuleButton()

                    Divider()

                    HStack {
                        Spacer()

                        Text(LocalizedStringResource.SignUp.alreadyHaveAccount)

                        Text(LocalizedStringResource.SignUp.loginText)
                            .bold()
                            .foregroundStyle(.accent)
                            .onTapGesture {
                                dismiss()
                            }

                        Spacer()
                    }

                }  //: VStack Container
                .padding()
            }  //: ScrollView
            .scrollDismissesKeyboard(.immediately)
        }  //: ZStack Background
        .onTapGesture {
            UIApplication.shared.sendAction(
                #selector(UIResponder.resignFirstResponder),
                to: nil,
                from: nil,
                for: nil
            )
        }
    }
}

#Preview {
    SignUpView()
}
