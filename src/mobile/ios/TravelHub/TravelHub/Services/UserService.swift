//
//  UserService.swift
//  TravelHub
//
//  Created by Andres Donoso on 29/03/26.
//

import Foundation

protocol UserService {

    /// Sends a request to create a new user
    ///
    /// - Parameters:
    ///     - user: The information of the user to create
    func create(user: NewUsuario) async throws -> Usuario

    /// Fetches the current authenticated user's profile
    func getMe() async throws -> MeResponse
}

final class UserServiceImpl: UserService {
    private let httpService: HttpService
    private let tokenStore: TokenStoring

    init(httpService: HttpService, tokenStore: TokenStoring = KeychainTokenStore.shared) {
        self.httpService = httpService
        self.tokenStore = tokenStore
    }

    func create(user: NewUsuario) async throws -> Usuario {
        let body = CreateUserRequest(
            email: user.email,
            password: user.password,
            nombre: user.nombre,
            telefono: user.telefono,
            tipo: user.tipo
        )

        let response: CreateUserResponse = try await self.httpService.post(
            url: HttpRoutes.usuarios.url,
            body: body
        )

        return Viajero(
            id: response.id,
            email: response.email,
            nombre: response.viajero.nombre,
            contacto: response.viajero.contacto
        )
    }

    func getMe() async throws -> MeResponse {
        let token = try tokenStore.readToken()
        return try await httpService.get(url: HttpRoutes.usuarioMe.url, token: token)
    }
}
