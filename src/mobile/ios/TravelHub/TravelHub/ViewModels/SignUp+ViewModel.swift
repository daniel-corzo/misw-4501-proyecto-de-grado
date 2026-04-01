//
//  SignUp+ViewModel.swift
//  TravelHub
//
//  Created by Andres Donoso on 19/03/26.
//

import SwiftUI

extension SignUpView {
    @Observable
    class ViewModel {
        var userService: UserService = UserServiceKey.defaultValue
        var toastManager: ToastManager = ToastManagerKey.defaultValue

        // MARK: - State Variables
        var fullName: String = ""
        var phone: String = ""
        var email: String = ""
        var password: String = ""
        var agreeToTerms: Bool = false

        // MARK: - Computed Properties

        var rawPhone: String {
            phone.filter { $0.isNumber }
        }

        var fullNameError: LocalizedStringResource? {
            if fullName.isEmpty {
                return .UserData.fullNameEmptyError
            }

            return nil
        }

        var phoneError: LocalizedStringResource? {
            if rawPhone.isEmpty {
                return .UserData.phoneIsEmptyError
            }

            if rawPhone.count < 10 {
                return .UserData.phoneIsInvalidError
            }

            return nil
        }

        var emailError: LocalizedStringResource? {
            if email.isEmpty {
                return .UserData.emailIsEmptyError
            }

            if !email.isEmpty && !email.isValidEmail {
                return .UserData.emailFormatIsInvalidError
            }

            return nil
        }

        var passwordErrors: [PasswordError] {
            return [
                password.contains(/\d+/) ? nil : .noNumbers,
                password.contains(/[\.\-\_]+/) ? nil : .noSymbols,
                password.count >= 8 ? nil : .tooShort,
                password.contains(/[a-z]+/) ? nil : .noLowercase,
                password.contains(/[A-Z]+/) ? nil : .noUppercase,
                password.isEmpty ? .empty : nil,
            ].compactMap(\.self)
        }

        var formIsValid: Bool {
            return fullNameError == nil && phoneError == nil
                && emailError == nil && passwordErrors.isEmpty && agreeToTerms
        }

        var fullNameSmallText: AttributedString {
            guard let fullNameError else {
                return ""
            }

            var smallText = AttributedString(localized: fullNameError)
            smallText.foregroundColor = .danger

            return smallText
        }

        var phoneSmallText: AttributedString {
            guard let phoneError else {
                return ""
            }

            var smallText = AttributedString(localized: phoneError)
            smallText.foregroundColor = .danger

            return smallText
        }

        var emailSmallText: AttributedString {
            guard let emailError else {
                return ""
            }

            var smallText = AttributedString(localized: emailError)
            smallText.foregroundColor = .danger

            return smallText
        }

        var passwordSmallText: AttributedString {
            var smallText: AttributedString = ""

            if password.isEmpty {
                var errorText = AttributedString(
                    localized: .UserData.passwordIsEmptyError
                )
                errorText.foregroundColor = .danger

                smallText += errorText + "\n\n"
            }

            smallText += buildPasswordRequirementsText()

            return smallText
        }

        // MARK: - Functions

        @MainActor
        func create(user: NewUsuario, dismiss: DismissAction) async {
            do {
                let _ = try await self.userService.create(user: user)
                toastManager.success(String(localized: .SignUp.userCreated))
                dismiss()
            } catch {
                toastManager.error(error.localizedDescription, title: "Error")
            }
        }

        private func buildPasswordRequirementsText()
            -> AttributedString
        {
            var description = AttributedString(
                localized: .UserData.passwordRequirementsDescription
            )
            description.foregroundColor = .neutralDark

            let minCharsText = formatPasswordRequirement(
                .UserData.passwordMinChar,
                isError: passwordErrors.contains(where: { $0 == .tooShort })
            )
            let numbersText = formatPasswordRequirement(
                .UserData.passwordNumber,
                isError: passwordErrors.contains(where: { $0 == .noNumbers })
            )
            let symbolsText = formatPasswordRequirement(
                .UserData.passwordSymbol,
                isError: passwordErrors.contains(where: { $0 == .noSymbols })
            )
            let lowerCaseText = formatPasswordRequirement(
                .UserData.passwordLowerCase,
                isError: passwordErrors.contains(where: { $0 == .noLowercase })
            )
            let upperCaseText = formatPasswordRequirement(
                .UserData.passwordUpperCase,
                isError: passwordErrors.contains(where: { $0 == .noUppercase })
            )

            return description
                + "\n\t" + minCharsText
                + "\n\t" + numbersText
                + "\n\t" + symbolsText
                + "\n\t" + lowerCaseText
                + "\n\t" + upperCaseText
        }

        private func formatPasswordRequirement(
            _ text: LocalizedStringResource,
            isError: Bool
        ) -> AttributedString {
            let attributedString = AttributedString(localized: text)
            let prefix = AttributedString(isError ? "✗ " : "✓ ")

            var finalText = prefix + attributedString
            finalText.foregroundColor = isError ? .danger : .success

            return finalText
        }
    }
}
