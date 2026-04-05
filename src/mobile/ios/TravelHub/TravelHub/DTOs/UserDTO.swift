//
//  UserDTO.swift
//  TravelHub
//
//  Created by Andres Donoso on 29/03/26.
//

import Foundation

// MARK: - User Creation

struct CreateUserRequest: Encodable {
    let email: String
    let password: String
    let nombre: String
    let telefono: String
    let tipo: TipoUsuario
}

struct CreateViajeroResponse: Decodable {
    let id: UUID
    let nombre: String
    let contacto: String
}

struct CreateUserResponse: Decodable {
    let id: UUID
    let email: String
    let tipo: TipoUsuario
    let viajero: CreateViajeroResponse
}

// MARK: - User Me

struct ViajeroMeResponse: Decodable {
    let id: UUID
    let nombre: String
    let contacto: String
}

struct MeResponse: Decodable {
    let id: UUID
    let tipo: String
    let email: String
    let role: String
    let viajero: ViajeroMeResponse?
}
