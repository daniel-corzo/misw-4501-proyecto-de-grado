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
}

final class UserServiceImpl: UserService {
    private let httpService: HttpService

    init(httpService: HttpService) {
        self.httpService = httpService
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
        
        if response.tipo == .viajero {
            return Viajero(id: response.id, email: response.email, nombre: response.viajero.nombre, contacto: response.viajero.contacto)
        }
        
        return Usuario(id: response.id, email: response.email, tipo: response.tipo)
    }
}
