import Foundation

struct LoginRequest: Codable {
    let email: String
    let password: String
}

struct LoginResponse: Codable {
    let accessToken: String
    let tokenType: String
    let expiresIn: Int

    // Keep compatibility with existing code using `response.token`
    var token: String { accessToken }

    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case tokenType = "token_type"
        case expiresIn = "expires_in"
    }
}

protocol AuthServicing {
    func logIn(email: String, password: String) async throws -> LoginResponse
}

enum AuthError: LocalizedError, Equatable {
    case invalidCredentials
    case server(String)
    case decoding
    case network
    case unknown

    var errorDescription: String? {
        switch self {
        case .invalidCredentials:
            return "Credenciales inválidas. Verifica tu correo y contraseña."
        case .server(let message):
            return message
        case .decoding:
            return "Error interpretando la respuesta del servidor."
        case .network:
            return "Problema de conexión. Inténtalo de nuevo."
        case .unknown:
            return "Ha ocurrido un error inesperado."
        }
    }
}

final class AuthService: AuthServicing {
    private let baseURL: URL
    private let urlSession: URLSession

    init(baseURL: URL = HttpRoutes.auth.url, urlSession: URLSession = .shared) {
        self.baseURL = baseURL
        self.urlSession = urlSession
    }

    func logIn(email: String, password: String) async throws -> LoginResponse {
        let endpoint = baseURL.appendingPathComponent("login")
        var request = URLRequest(url: endpoint)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        let body = LoginRequest(email: email, password: password)
        request.httpBody = try JSONEncoder().encode(body)

        do {
            let (data, response) = try await urlSession.data(for: request)
            guard let http = response as? HTTPURLResponse else { throw AuthError.unknown }

            switch http.statusCode {
            case 200...299:
                do {
                    return try JSONDecoder().decode(LoginResponse.self, from: data)
                } catch {
                    throw AuthError.decoding
                }
            case 401:
                throw AuthError.invalidCredentials
            default:
                // Try to parse server error message
                if let message = try? JSONDecoder().decode([String: String].self, from: data)["message"] {
                    throw AuthError.server(message)
                } else {
                    throw AuthError.server("Error del servidor (\(http.statusCode)).")
                }
            }
        } catch let error as AuthError {
            throw error
        } catch {
            // Map common URLSession errors
            if (error as NSError).domain == NSURLErrorDomain { return try await mapNetworkError(error) }
            throw AuthError.unknown
        }
    }

    private func mapNetworkError(_ error: Error) async throws -> LoginResponse {
        throw AuthError.network
    }
}
