//
//  TravelHubApp.swift
//  TravelHub
//
//  Created by Andres Donoso on 17/03/26.
//

import SwiftUI

extension EnvironmentValues {
    var userService: UserService {
        get { self[UserServiceKey.self] }
        set { self[UserServiceKey.self] = newValue }
    }
}

struct UserServiceKey: EnvironmentKey {
    static let defaultValue: UserService = UserServiceImpl(httpService: HttpServiceImpl.shared)
}

@main
struct TravelHubApp: App {
    @State private var toastManager = ToastManager()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.userService, UserServiceImpl(httpService: HttpServiceImpl.shared))
                .environment(\.toastManager, toastManager)
                .toastOverlay(toastManager: toastManager)
        }
    }
}
