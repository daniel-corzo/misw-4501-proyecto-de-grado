//
//  HttpService.swift
//  TravelHub
//
//  Created by Andres Donoso on 29/03/26.
//

import Foundation

enum HttpError: LocalizedError, Equatable {
    case invalidCredentials
    case server(String)
    case decoding
    case network
    case unknown
    
    var errorDescription: String? {
        switch self {
            case .invalidCredentials:
                return String(localized: .HttpErrors.invalidCredentials)
            case .server(let message):
                return String(localized: .HttpErrors.server(serverError: message))
            case .decoding:
                return String(localized: .HttpErrors.decoding)
            case .network:
                return String(localized: .HttpErrors.network)
            case .unknown:
                return String(localized: .HttpErrors.unknown)
        }
    }
}

protocol HttpService {
    /// Sends a POST request with the given body
    ///
    /// - Parameters:
    ///     - url: The URL to which the request will be made
    ///     - body: The request's body
    ///
    func post<T: Encodable, V: Decodable>(url: URL, body: T) async throws -> V
}
