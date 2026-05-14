//
//  TravelHubApp.swift
//  TravelHub
//
//  Created by Andres Donoso on 17/03/26.
//

import SwiftUI
import UserNotifications

@main
struct TravelHubApp: App {
    @State private var toastManager = ToastManager()
    @State private var router = Router()
    @State private var bookingPoller = BookingPollerService()

    private let notificationDelegate = NotificationDelegate()

    init() {
        UNUserNotificationCenter.current().delegate = notificationDelegate
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.userService, UserServiceImpl(httpService: HttpServiceImpl.shared))
                .environment(\.authService, AuthServiceImpl(httpService: HttpServiceImpl.shared))
                .environment(\.hotelService, HotelServiceImpl(httpService: HttpServiceImpl.shared))
                .environment(\.bookingService, BookingServiceImpl(httpService: HttpServiceImpl.shared))
                .environment(\.paymentService, PaymentServiceKey.defaultValue)
                .environment(\.bookingPoller, bookingPoller)
                .environment(\.toastManager, toastManager)
                .toastOverlay(toastManager: toastManager)
                .environment(router)
                .task {
                    try? await UNUserNotificationCenter.current()
                        .requestAuthorization(options: [.alert, .sound])
                }
        }
    }
}
