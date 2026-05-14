//
//  MainView.swift
//  TravelHub
//
//  Created by Germán Martínez Solano on 23/03/26.
//

import SwiftUI

struct MainView: View {

    @Environment(Router.self) private var router
    @Environment(\.bookingService) private var bookingService
    @Environment(\.bookingPoller) private var poller

    @Binding var isLoggedIn: Bool

    var body: some View {
        NavigationStack(path: Bindable(router).path.animation()) {
            TabView(selection: Bindable(router).selectedTab) {
                ListHotelView()
                    .tabItem {
                        Label(
                            LocalizedStringResource.TabBar.explore,
                            systemImage: "safari"
                        )
                    }
                    .tag(Tab.explore)

                MyBookingsView()
                    .tabItem {
                        Label(
                            LocalizedStringResource.TabBar.bookings,
                            systemImage: "calendar"
                        )
                    }
                    .tag(Tab.bookings)

                ProfileView(isLoggedIn: $isLoggedIn)
                    .tabItem {
                        Label(
                            LocalizedStringResource.TabBar.profile,
                            systemImage: "person"
                        )
                    }
                    .tag(Tab.profile)
            }
            .navigationDestination(for: Destination.self) { destination in
                switch destination {
                    case .myBookings: MyBookingsView()
                    case .createBooking(let hotel, let booking):
                        CreateBookingView(hotel: hotel, booking: booking)
                    case .hotelDetail(let id):
                        HotelDetailView(hotelId: id)
                }
            }
        }
        .task {
            await poller.start(bookingService: bookingService)
        }
    }

}

#Preview {
    MainView(isLoggedIn: .constant(true))
}
