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
    case usuarioMe
    case login
    case logout
    case hoteles
    case reservas
    
    var url: URL {
        switch self {
            case .login:
                return AppConfig.baseURL.appendingPathComponent("auth/login")
            
            case .logout:
                return AppConfig.baseURL.appendingPathComponent("auth/logout")
            
            case .hoteles:
                return AppConfig.baseURL.appendingPathComponent("hoteles")
                
            case .usuarios:
                return AppConfig.baseURL.appendingPathComponent("usuarios")
            
            case .usuarioMe:
                return AppConfig.baseURL.appendingPathComponent("usuarios/me")
                
            case .reservas:
                return AppConfig.baseURL.appendingPathComponent("reservas")
        }
    }
}

