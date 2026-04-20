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

struct NewReservation {
    var habitacionID: UUID
    var fechaEntrada: Date
    var fechaSalida: Date
    var numHuespedes: Int
    var pagoID: UUID?
}
