//
//  HttpServiceImpl.swift
//  TravelHub
//
//  Created by Andres Donoso on 29/03/26.
//

import Foundation

final class HttpServiceImpl: HttpService {
    static let shared = HttpServiceImpl()
    
    private init() {}
    
    func post<T: Encodable, V: Decodable>(url: URL, body: T) async throws -> V {
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(body)
        
        do {
            let (data, response) = try await URLSession.shared.data(for: request)
            guard let http = response as? HTTPURLResponse else { throw HttpError.unknown }
            
            switch http.statusCode {
                case 200...299:
                    do {
                        return try JSONDecoder().decode(V.self, from: data)
                    } catch {
                        throw HttpError.decoding
                    }
                case 401:
                    throw HttpError.invalidCredentials
                default:
                    // Try to parse server error message
                    if let message = try? JSONDecoder().decode([String: String].self, from: data)["detail"] {
                        throw HttpError.server(message)
                    } else {
                        throw HttpError.server("Error del servidor (\(http.statusCode)).")
                    }
            }
        } catch let error as HttpError {
            throw error
        } catch {
            print(error)
            throw HttpError.unknown
        }
    }
}
