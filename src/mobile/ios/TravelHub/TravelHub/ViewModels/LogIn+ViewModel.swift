//
//  LogInView+ViewModel.swift
//  TravelHub
//
//  Created by Germán Martínez Solano on 19/03/26.
//

import Foundation

extension LogInView {
    @Observable
    class ViewModel {
        // MARK: - State Variables
        var email: String = ""
        var password: String = ""
        
        // MARK: - Computed Properties
        
        var emailIsValid: Bool {
            !email.isEmpty && email.contains("@")
        }
    }
}
