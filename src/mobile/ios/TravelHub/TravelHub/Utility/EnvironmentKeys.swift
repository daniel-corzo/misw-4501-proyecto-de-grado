//
//  EnvironmentKeys.swift
//  TravelHub
//
//  Created by Andres Donoso on 29/03/26.
//

import SwiftUI

// MARK: - Environment Keys
struct ToastManagerKey: EnvironmentKey {
    static let defaultValue = ToastManager()
}

struct UserServiceKey: EnvironmentKey {
    static let defaultValue: UserService = UserServiceImpl(httpService: HttpServiceImpl.shared)
}

struct AuthServiceKey: EnvironmentKey {
    static let defaultValue: AuthServicing = AuthService(httpService: HttpServiceImpl.shared)
}

// MARK: - Environment Values
extension EnvironmentValues {
    // MARK: Toast Manager
    var toastManager: ToastManager {
        get { self[ToastManagerKey.self] }
        set { self[ToastManagerKey.self] = newValue }
    }
    
    // MARK: User Service
    var userService: UserService {
        get { self[UserServiceKey.self] }
        set { self[UserServiceKey.self] = newValue }
    }
    
    // MARK: Auth Service
    var authService: AuthServicing {
        get { self[AuthServiceKey.self] }
        set { self[AuthServiceKey.self] = newValue }
    }
}
