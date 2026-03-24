//
//  MainView.swift
//  TravelHub
//
//  Created by Germán Martínez Solano on 23/03/26.
//

import SwiftUI

struct MainView: View {
    
    @State private var selectedTab: CustomTabBar.Tab = .explore
    
    var body: some View {
        ZStack {
            
            Group {
                switch selectedTab {
                case .explore:
                    NavigationStack {
                        ListHotelView()
                    }
                    
                case .bookings:
                    NavigationStack {
                        Text("Bookings View")
                    }
                    
                case .profile:
                    NavigationStack {
                        Text("Profile View")
                    }
                }
            }
            
            VStack {
                Spacer()
                CustomTabBar(selectedTab: $selectedTab)
            }
        }
    }
}

#Preview {
    MainView()
}
