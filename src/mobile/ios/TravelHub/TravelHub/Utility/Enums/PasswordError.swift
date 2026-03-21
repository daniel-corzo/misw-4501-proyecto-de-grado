//
//  PasswordError.swift
//  TravelHub
//
//  Created by Andres Donoso on 21/03/26.
//

import Foundation

enum PasswordError {
    case empty, tooShort, noNumbers, noSymbols, noLowercase, noUppercase

    var description: LocalizedStringResource {
        switch self {
            case .empty:
                return .UserData.passwordIsEmptyError

            case .noLowercase:
                return .UserData.passwordLowerCase

            case .noUppercase:
                return .UserData.passwordUpperCase

            case .noNumbers:
                return .UserData.passwordNumber

            case .noSymbols:
                return .UserData.passwordSymbol
                
            case .tooShort:
                return .UserData.passwordMinChar
        }
    }
}
