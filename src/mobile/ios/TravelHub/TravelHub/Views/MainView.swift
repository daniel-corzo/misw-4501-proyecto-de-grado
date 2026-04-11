//
//  MainView.swift
//  TravelHub
//
//  Created by Germán Martínez Solano on 23/03/26.
//

import SwiftUI

struct MainView: View {

    @Binding var isLoggedIn: Bool

    var body: some View {
        TabView {
            
            NavigationStack {
                ListHotelView()
            }
            .tabItem {
                Label(LocalizedStringResource.TabBar.explore, systemImage: "safari")
            }
            
            NavigationStack {
                Text("Bookings View")
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
