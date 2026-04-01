//
//  TravelHubApp.swift
//  TravelHub
//
//  Created by Andres Donoso on 17/03/26.
//

import SwiftUI

@main
struct TravelHubApp: App {
    @State private var toastManager = ToastManager()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.userService, UserServiceImpl(httpService: HttpServiceImpl.shared))
                .environment(\.authService, AuthService(httpService: HttpServiceImpl.shared))
                .environment(\.toastManager, toastManager)
                .toastOverlay(toastManager: toastManager)
        }
    }
}
