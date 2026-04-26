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
        TabView {
            
            NavigationStack(path: Bindable(router).path) {
                ListHotelView()
                    .navigationDestination(for: Destination.self) { destination in
                        switch destination {
                            case .myBookings: MyBookingsView()
                        }
                    }
            }
            .tabItem {
                Label(LocalizedStringResource.TabBar.explore, systemImage: "safari")
            }
            
            NavigationStack {
                MyBookingsView()
            }
            .tabItem {
                Label(LocalizedStringResource.TabBar.bookings, systemImage: "calendar")
            }
            
            NavigationStack {
                ProfileView(isLoggedIn: $isLoggedIn)
            }
            .tabItem {
                Label(LocalizedStringResource.TabBar.profile, systemImage: "person")
            }
        }
    }
}

#Preview {
    MainView(isLoggedIn: .constant(true))
}
