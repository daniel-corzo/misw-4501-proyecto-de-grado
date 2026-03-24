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

        var fullNameSmallText: AttributedString {
            let errors: [LocalizedStringResource] = [
                fullName.isEmpty ? .UserData.fullNameEmptyError : nil
            ].compactMap(\.self)

            var smallText = errors.joinToAttributedString(with: "")
            smallText.foregroundColor = .danger

            return smallText
        }

        var phoneSmallText: AttributedString {
            var error: LocalizedStringResource = ""
            
            if rawPhone.isEmpty {
                error = .UserData.emailIsEmptyError
            }
            
            if rawPhone.count < 10 {
                error = .UserData.phoneIsInvalidError
            }

            var smallText = AttributedString(localized: error)
            smallText.foregroundColor = .danger

            return smallText
        }

        var emailSmallText: AttributedString {
            var error: LocalizedStringResource = ""
            
            if email.isEmpty {
                error = .UserData.emailIsEmptyError
            }
            
            if !email.isEmpty && !email.isValidEmail {
                error = .UserData.emailFormatIsInvalidError
            }

            var smallText = AttributedString(localized: error)
            smallText.foregroundColor = .danger

            return smallText
        }

        var passwordSmallText: AttributedString {
            let errors: [PasswordError] = [
                password.contains(/\d+/) ? nil : .noNumbers,
                password.contains(/[\.\-\_]+/) ? nil : .noSymbols,
                password.count >= 8 ? nil : .tooShort,
                password.contains(/[a-z]+/) ? nil : .noLowercase,
                password.contains(/[A-Z]+/) ? nil : .noUppercase,
            ].compactMap(\.self)

            var smallText: AttributedString = ""

            if password.isEmpty {
                var errorText = AttributedString(
                    localized: .UserData.passwordIsEmptyError
                )
                errorText.foregroundColor = .danger

                smallText += errorText + "\n\n"
            }
            
            smallText += buildPasswordRequirementsText(errors: errors)

            return smallText
        }

        // MARK: - Functions

        private func buildPasswordRequirementsText(errors: [PasswordError])
            -> AttributedString
        {
            var description = AttributedString(
                localized: .UserData.passwordRequirementsDescription
            )
            description.foregroundColor = .neutralDark

            let minCharsText = formatPasswordRequirement(
                .UserData.passwordMinChar,
                isError: errors.contains(where: { $0 == .tooShort })
            )
            let numbersText = formatPasswordRequirement(
                .UserData.passwordNumber,
                isError: errors.contains(where: { $0 == .noNumbers })
            )
            let symbolsText = formatPasswordRequirement(
                .UserData.passwordSymbol,
                isError: errors.contains(where: { $0 == .noSymbols })
            )
            let lowerCaseText = formatPasswordRequirement(
                .UserData.passwordLowerCase,
                isError: errors.contains(where: { $0 == .noLowercase })
            )
            let upperCaseText = formatPasswordRequirement(
                .UserData.passwordUpperCase,
                isError: errors.contains(where: { $0 == .noUppercase })
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
