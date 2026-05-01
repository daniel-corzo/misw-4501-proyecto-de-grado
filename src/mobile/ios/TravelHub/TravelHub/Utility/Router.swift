//
//  Router.swift
//  TravelHub
//
//  Created by Andres Donoso on 26/04/26.
//

import SwiftUI

@Observable
class Router {
    var path = NavigationPath()
    var selectedTab: Tab = .explore
    var pendingBookingTab: BookingTab?

    func navigate(to destination: Destination) {
        path.append(destination)
    }

    func navigateWithoutHistory(to destination: Destination) {
        path = NavigationPath()          // 👈 clears history
        path.append(destination)
    }

    func switchTab(to tab: Tab) {
        path = NavigationPath()  // 👈 clears any stack history
        selectedTab = tab
    }
}

enum Tab {
    case explore, bookings, profile
}

enum Destination: Hashable {
    case myBookings
    case createBooking(Hotel, ModifyBooking?)
    case hotelDetail(UUID)
}
