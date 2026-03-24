//
//  ContentView.swift
//  TravelHub
//
//  Created by Andres Donoso on 17/03/26.
//

import SwiftUI

struct ContentView: View {
    
    @State private var isLoggedIn = false
    
    var body: some View {
        if isLoggedIn {
            MainView()
        } else {
            NavigationStack {
                LogInView(isLoggedIn: $isLoggedIn)
            }
        }
    }
}

#Preview {
    ContentView()
}
