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

// MARK: - Modify Reservation
struct ModifyReservationRequest: Encodable {
    var fechaEntrada: String?
    var fechaSalida: String?
    var numHuespedes: Int?
    var habitacionId: UUID?

    enum CodingKeys: String, CodingKey {
        case fechaEntrada = "fecha_entrada"
        case fechaSalida = "fecha_salida"
        case numHuespedes = "num_huespedes"
        case habitacionId = "habitacion_id"
    }
}

struct ModifyReservationResponse: Decodable {
    var id: UUID
    var habitacionId: UUID
    var nombreHabitacion: String?
    var nombreHotel: String?
    var imagenesHotel: [String]
    var ciudadHotel: String?
    var paisHotel: String?
    var fechaEntrada: String
    var fechaSalida: String
    var numHuespedes: Int
    var estado: EstadoReserva
    var pagoId: UUID?
    var createdAt: String

    enum CodingKeys: String, CodingKey {
        case id
        case habitacionId = "habitacion_id"
        case nombreHabitacion = "nombre_habitacion"
        case nombreHotel = "nombre_hotel"
        case imagenesHotel = "imagenes_hotel"
        case ciudadHotel = "ciudad_hotel"
        case paisHotel = "pais_hotel"
        case fechaEntrada = "fecha_entrada"
        case fechaSalida = "fecha_salida"
        case numHuespedes = "num_huespedes"
        case estado
        case pagoId = "pago_id"
        case createdAt = "created_at"
    }
}

// MARK: - List Reservations

struct ListReservationsResponse: Decodable {
    let total: Int
    let reservas: [ReservationListItemDTO]
}

struct ReservationListItemDTO: Decodable, Identifiable {
    let id: UUID
    let habitacionId: UUID
    let nombreHabitacion: String?
    let nombreHotel: String?
    let imagenesHotel: [String]
    let fechaEntrada: String
    let fechaSalida: String
    let numHuespedes: Int
    let estado: EstadoReserva
    let pagoId: UUID?
    let createdAt: String

    enum CodingKeys: String, CodingKey {
        case id, estado
        case habitacionId = "habitacion_id"
        case nombreHabitacion = "nombre_habitacion"
        case nombreHotel = "nombre_hotel"
        case imagenesHotel = "imagenes_hotel"
        case fechaEntrada = "fecha_entrada"
        case fechaSalida = "fecha_salida"
        case numHuespedes = "num_huespedes"
        case pagoId = "pago_id"
        case createdAt = "created_at"
    }
}

// MARK: - Reservation Detail

struct ReservationDetailDTO: Decodable, Identifiable {
    let id: UUID
    let codigoReserva: String
    let estado: EstadoReserva
    let fechaEntrada: String
    let fechaSalida: String
    let numHuespedes: Int
    let pagoId: UUID?
    let createdAt: String
    let hotel: ReservationHotelDTO
    let habitacion: ReservationRoomDTO
    let amenidadesHotel: [String]

    enum CodingKeys: String, CodingKey {
        case id, estado, hotel, habitacion
        case codigoReserva = "codigo_reserva"
        case fechaEntrada = "fecha_entrada"
        case fechaSalida = "fecha_salida"
        case numHuespedes = "num_huespedes"
        case pagoId = "pago_id"
        case createdAt = "created_at"
        case amenidadesHotel = "amenidades_hotel"
    }
}

struct ReservationHotelDTO: Decodable {
    let id: UUID?
    let nombre: String
    let direccion: String?
    let ciudad: String?
    let pais: String?
    let estrellas: Int?
    let ranking: Double?
    let imagenes: [String]
    let contactoCelular: String?
    let contactoEmail: String?
    let checkIn: String?
    let checkOut: String?

    enum CodingKeys: String, CodingKey {
        case id, nombre, direccion, ciudad, pais, estrellas, ranking, imagenes
        case contactoCelular = "contacto_celular"
        case contactoEmail = "contacto_email"
        case checkIn = "check_in"
        case checkOut = "check_out"
    }

    func toHotel() -> Hotel {
        return Hotel(
            id: id ?? UUID(),
            nombre: nombre,
            direccion: direccion ?? "",
            pais: pais ?? "",
            estado: nil,
            departamento: "",
            ciudad: ciudad ?? "",
            descripcion: "",
            amenidades: [],
            estrellas: estrellas ?? 1,
            ranking: ranking ?? 0,
            contactoCelular: contactoCelular ?? "",
            contactoEmail: contactoEmail ?? "",
            images: imagenes,
            checkInHour: checkIn ?? .init(),
            checkOutHour: checkOut ?? .init(),
            valorMinimoModificacion: 0,
            politicas: [],
            habitaciones: [],
            precioMinimo: 0
        )
    }
}

struct ReservationRoomDTO: Decodable {
    let id: UUID
    let nombre: String
    let descripcion: String?
    let numero: String?
    let capacidad: Int?
    let imagenes: [String]
    let monto: Int?
    let impuestos: Int?
}
