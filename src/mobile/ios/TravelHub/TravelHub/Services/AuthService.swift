import Foundation

protocol AuthService {
    func logIn(email: String, password: String) async throws -> LoginResponse
    func logOut(token: String?) async throws -> LogoutResponse
}

final class AuthServiceImpl: AuthService {
    private let httpService: HttpService
    
    init(httpService: HttpService) {
        self.httpService = httpService
    }

    func logIn(email: String, password: String) async throws -> LoginResponse {
        let body = LoginRequest(email: email, password: password)
        return try await self.httpService.post(url: HttpRoutes.login.url, body: body)
    }

    func logOut(token: String?) async throws -> LogoutResponse {
        return try await self.httpService.post(url: HttpRoutes.logout.url, token: token)
    }
}
