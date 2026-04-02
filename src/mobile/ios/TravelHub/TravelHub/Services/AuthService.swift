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

final class AuthService: AuthServicing {
    private let httpService: HttpService
    
    init(httpService: HttpService) {
        self.httpService = httpService
    }

    func logIn(email: String, password: String) async throws -> LoginResponse {
        let body = LoginRequest(email: email, password: password)
        return try await self.httpService.post(url: HttpRoutes.login.url, body: body)
    }
}
