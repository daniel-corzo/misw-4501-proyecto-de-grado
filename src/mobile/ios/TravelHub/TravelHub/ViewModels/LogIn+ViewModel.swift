//
//  LogInView+ViewModel.swift
//  TravelHub
//
//  Created by Germán Martínez Solano on 19/03/26.
//

import SwiftUI

extension LogInView {
    @Observable
    class ViewModel {
        var authService: AuthServicing = AuthServiceKey.defaultValue
        
        // MARK: - State Variables
        var email: String = ""
        var password: String = ""
        private let tokenStore: TokenStoring

        // MARK: - Init
        init(tokenStore: TokenStoring = KeychainTokenStore.shared) {
            self.tokenStore = tokenStore
        }

        // MARK: - Computed Properties
        var canSubmit: Bool {
            !email.isEmpty && !password.isEmpty
        }

        // MARK: - Actions
        @MainActor
        func logIn() async throws -> LoginResponse {
            guard !email.isEmpty, !password.isEmpty else {
                throw HttpError.server("Por favor, completa correo y contraseña.")
            }

            do {
                let response = try await authService.logIn(email: email, password: password)
                do {
                    try tokenStore.save(token: response.token)
                } catch {
                    throw HttpError.server("No se pudo guardar el token de sesión")
                }
                
                return response
            } catch {
                throw error
            }
        }
    }
}

