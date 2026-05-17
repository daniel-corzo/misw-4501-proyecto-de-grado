//
//  EstadoReserva.swift
//  TravelHub
//
//  Created by Andres Donoso on 18/04/26.
//

import Foundation

enum EstadoReserva: String, Codable {
    case pendiente = "pendiente"
    case confirmada = "confirmada"
    case cancelada = "cancelada"
    case completada = "completada"
}

// MARK: - Utility Models

struct NewBooking {
    var habitacionID: UUID
    var fechaEntrada: Date
    var fechaSalida: Date
    var numHuespedes: Int
    var pagoID: UUID?
}

struct ModifyBooking: Hashable {
    var id: UUID
    var habitacionID: UUID
    var fechaEntrada: Date
    var fechaSalida: Date
    var numHuespedes: Int
}
