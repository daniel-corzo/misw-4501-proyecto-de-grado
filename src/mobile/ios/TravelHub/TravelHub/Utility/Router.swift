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
    
    func navigate(to destination: Destination) {
        path.append(destination)
    }
    
    func navigateWithoutHistory(to destination: Destination) {
        path = NavigationPath()          // 👈 clears history
        path.append(destination)
    }
}

enum Destination: Hashable {
    case myBookings
}
