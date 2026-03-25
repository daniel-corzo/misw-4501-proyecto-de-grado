//
//  MainView.swift
//  TravelHub
//
//  Created by Germán Martínez Solano on 23/03/26.
//

import SwiftUI

struct MainView: View {
    
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
                Text("Profile View")
            }
            .tabItem {
                Label(LocalizedStringResource.TabBar.profile, systemImage: "person")
            }
        }
    }
}

#Preview {
    MainView()
}
