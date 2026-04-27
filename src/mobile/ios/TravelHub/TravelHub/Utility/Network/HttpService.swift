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

    /// Sends a POST request with an authorization token and no body
    ///
    /// - Parameters:
    ///     - url: The URL to which the request will be made
    ///     - token: The bearer token for authorization
    ///
    func post<V: Decodable>(url: URL, token: String?) async throws -> V
    
    /// Sends a POST request with an authorization token and body
    ///
    /// - Parameters:
    ///     - url: The URL to which the request will be made
    ///     - token: The bearer token for authorization
    ///     - body: The request's body
    func post<T: Encodable, V: Decodable>(url: URL, body: T, token: String) async throws -> V

    /// Sends a GET request
    ///
    /// - Parameters:
    ///     - url: The URL to which the request will be made
    ///
    func get<V: Decodable>(url: URL, token: String?) async throws -> V

    /// Sends a PATCH request with an authorization token and no body
    ///
    /// - Parameters:
    ///     - url: The URL to which the request will be made
    ///     - token: The bearer token for authorization
    ///
    func patch<V: Decodable>(url: URL, token: String) async throws -> V
    
    /// Sends a PATCH request with an authorization token and body
    ///
    /// - Parameters:
    ///     - url: The URL to which the request will be made
    ///     - token: The bearer token for authorization
    ///     - body: The request's body
    func patch<T: Encodable, V: Decodable>(url: URL, token: String, body: T) async throws -> V
}

