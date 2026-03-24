//
//  TabBar.swift
//  TravelHub
//
//  Created by Germán Martínez Solano on 23/03/26.
//

import SwiftUI

struct CustomTabBar: View {
    
    @Binding var selectedTab: Tab
    
    enum Tab {
        case explore
        case bookings
        case profile
    }
    
    var body: some View {
        HStack {
            tabItem(icon: "safari", title: "Explore", tab: .explore)
            Spacer()
            tabItem(icon: "calendar", title: "Bookings", tab: .bookings)
            Spacer()
            tabItem(icon: "person", title: "Profile", tab: .profile)
        }
        .padding(.horizontal, 30)
        .padding(.vertical, 12)
        .background(Color(.systemBackground))
    }
    
    @ViewBuilder
    private func tabItem(icon: String, title: String, tab: Tab) -> some View {
        Button {
            selectedTab = tab
        } label: {
            VStack(spacing: 4) {
                Image(systemName: icon)
                    .font(.system(size: 18))
                
                Text(title)
                    .font(.caption)
            }
            .foregroundColor(selectedTab == tab ? .blue : .gray)
        }
    }
}
