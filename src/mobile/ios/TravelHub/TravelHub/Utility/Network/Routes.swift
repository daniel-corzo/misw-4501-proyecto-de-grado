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
    case auth
    
    var url: URL {
        switch self {
            case .auth:
                return AppConfig.baseURL.appendingPathComponent("auth")
                
            case .usuarios:
                return AppConfig.baseURL.appendingPathComponent("usuarios")
        }
    }
}
