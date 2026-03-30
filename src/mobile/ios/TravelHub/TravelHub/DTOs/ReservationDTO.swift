//
//  ReservationDTO.swift
//  TravelHub
//
//  Created by Andres Donoso on 18/04/26.
//

import Foundation

struct CreateReservationRequest: Encodable {
    var habitacionID: UUID
    var fechaEntrada: String
    var fechaSalida: String
    var numHuespedes: Int
    var pagoID: UUID?
    
    enum CodingKeys: String, CodingKey {
        case habitacionID = "habitacion_id"
        case fechaEntrada = "fecha_entrada"
        case fechaSalida = "fecha_salida"
        case numHuespedes = "num_huespedes"
        case pagoID = "pago_id"
    }
}

struct CreateReservationResponse: Decodable {
    var id: UUID
    var habitacionId: UUID
    var fechaEntrada: String
    var fechaSalida: String
    var numHuespedes: Int
    var estado: EstadoReserva
    var pagoId: UUID?
    var createdAt: String
    
    enum CodingKeys: String, CodingKey {
        case id, estado
        case habitacionId = "habitacion_id"
        case fechaEntrada = "fecha_entrada"
        case fechaSalida = "fecha_salida"
        case numHuespedes = "num_huespedes"
        case pagoId = "pago_id"
        case createdAt = "created_at"
    }
}
