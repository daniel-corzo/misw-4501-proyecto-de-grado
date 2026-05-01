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
    @State private var router = Router()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.userService, UserServiceImpl(httpService: HttpServiceImpl.shared))
                .environment(\.authService, AuthServiceImpl(httpService: HttpServiceImpl.shared))
                .environment(\.hotelService, HotelServiceImpl(httpService: HttpServiceImpl.shared))
                .environment(\.bookingService, BookingServiceImpl(httpService: HttpServiceImpl.shared))
                .environment(\.toastManager, toastManager)
                .toastOverlay(toastManager: toastManager)
                .environment(router)
        }
    }
}
