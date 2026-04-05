//
//  Profile+ViewModel.swift
//  TravelHub
//

import SwiftUI

extension ProfileView {
    @Observable
    class ViewModel {
        var userService: UserService = UserServiceKey.defaultValue
        var authService: AuthService = AuthServiceKey.defaultValue

        // MARK: - State Variables
        var userName: String = ""
        var email: String = ""
        var contacto: String = ""
        var isLoading: Bool = false

        private let tokenStore: TokenStoring

        // MARK: - Init
        init(tokenStore: TokenStoring = KeychainTokenStore.shared) {
            self.tokenStore = tokenStore
        }

        // MARK: - Actions
        @MainActor
        func fetchProfile(toastManager: ToastManager) async {
            isLoading = true
            defer { isLoading = false }
            do {
                let response = try await userService.getMe()
                userName = response.viajero?.nombre ?? ""
                email = response.email
                contacto = response.viajero?.contacto ?? ""
            } catch is CancellationError {
                return
            } catch {
                toastManager.error(error.localizedDescription)
            }
        }

        @MainActor
        func logOut() async throws {
            let token = try tokenStore.readToken()
            if let token {
                _ = try? await authService.logOut(token: token)
            }
            try tokenStore.deleteToken()
        }
    }
}
