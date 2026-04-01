//
//  Usuario.swift
//  TravelHub
//
//  Created by Andres Donoso on 29/03/26.
//

import Foundation

enum TipoUsuario: String, Codable {
    case viajero = "viajero"
    case hotel = "hotel"
}

class Usuario {
    let id: UUID
    let email: String
    let tipo: TipoUsuario
    
    init(id: UUID, email: String, tipo: TipoUsuario) {
        self.id = id
        self.email = email
        self.tipo = tipo
    }
}

class Viajero: Usuario {
    let nombre: String
    let contacto: String
    
    init(id: UUID, email: String, nombre: String, contacto: String) {
        self.nombre = nombre
        self.contacto = contacto
        
        super.init(id: id, email: email, tipo: .viajero)
    }
}

// MARK: - Utility models

struct NewUsuario {
    let email: String
    let password: String
    let nombre: String
    let telefono: String
    let tipo: TipoUsuario
}
