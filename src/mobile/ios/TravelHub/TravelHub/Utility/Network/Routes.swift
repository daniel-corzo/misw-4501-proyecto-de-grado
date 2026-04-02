//
//  Routes.swift
//  TravelHub
//
//  Created by Andres Donoso on 29/03/26.
//

import Foundation

/// A bookmark of the available routes
enum HttpRoutes {
    case usuarios
    case login
    
    var url: URL {
        switch self {
            case .login:
                return AppConfig.baseURL.appendingPathComponent("auth/login")
                
            case .usuarios:
                return AppConfig.baseURL.appendingPathComponent("usuarios")
        }
    }
}
