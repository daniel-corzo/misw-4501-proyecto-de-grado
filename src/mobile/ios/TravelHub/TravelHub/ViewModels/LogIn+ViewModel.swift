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
        // MARK: - State Variables
        var email: String = ""
        var password: String = ""
        var errorMessage: LocalizedStringResource?
        private let authService: AuthServicing
        private let tokenStore: TokenStoring

        // MARK: - Init
        init(authService: AuthServicing = AuthService(), tokenStore: TokenStoring = KeychainTokenStore.shared) {
            self.authService = authService
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
                throw AuthError.server("Por favor, completa correo y contraseña.")
            }

            do {
                let response = try await authService.logIn(email: email, password: password)
                do {
                    try tokenStore.save(token: response.token)
                } catch {
                    // Reflect token saving issue in UI but do not block login flow
                    errorMessage = LocalizedStringResource(stringLiteral: "No se pudo guardar el token de sesión.")
                }
                errorMessage = nil
                return response
            } catch let authError as AuthError {
                errorMessage = LocalizedStringResource(stringLiteral: authError.localizedDescription)
                throw authError
            } catch {
                errorMessage = LocalizedStringResource(stringLiteral: error.localizedDescription)
                throw error
            }
        }
    }
}

