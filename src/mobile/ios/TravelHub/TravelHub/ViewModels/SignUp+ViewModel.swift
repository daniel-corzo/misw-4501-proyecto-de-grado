//
//  SignUp+ViewModel.swift
//  TravelHub
//
//  Created by Andres Donoso on 19/03/26.
//

import Foundation

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
        
        var fullNameIsValid: Bool {
            !fullName.isEmpty
        }
        
        var phoneIsValid: Bool {
            !phone.isEmpty && rawPhone.count == 10
        }
        
        var emailIsValid: Bool {
            !email.isEmpty && email.contains("@")
        }
    }
}
