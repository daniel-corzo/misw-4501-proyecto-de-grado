//
//  MainView.swift
//  TravelHub
//
//  Created by Germán Martínez Solano on 23/03/26.
//

import SwiftUI

struct MainView: View {

    @Environment(Router.self) private var router

    @Binding var isLoggedIn: Bool

    var body: some View {
        NavigationStack(path: Bindable(router).path.animation()) {
            TabView {
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
                    case .createReservation(let hotel, let reservation):
                        CreateReservationView(hotel: hotel, reservation: reservation)
                    case .hotelDetail(let id):
                        HotelDetailView(hotelId: id)
                }
            }
        }
    }

}

#Preview {
    MainView(isLoggedIn: .constant(true))
}
