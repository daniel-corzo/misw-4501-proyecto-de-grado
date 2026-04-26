import Foundation

/// Respuesta para el listado de hoteles
struct HotelsResponseDTO: Decodable {
    let total: Int
    let hoteles: [HotelListDTO]
}

/// DTO que representa un hotel según la respuesta del backend
struct HotelListDTO: Decodable {
    let id: UUID
    let nombre: String
    let ciudad: String
    let pais: String
    let estrellas: Int
    let imagenes: [String]
    let precioMinimo: Int
    let createdAt: String

    enum CodingKeys: String, CodingKey {
        case id
        case nombre
        case ciudad
        case pais
        case estrellas
        case imagenes
        case precioMinimo = "precio_minimo"
        case createdAt = "created_at"
    }
}

/// DTO para la respuesta de detalle de un hotel
struct HotelDetailDTO: Decodable {
    let id: UUID
    let nombre: String
    let direccion: String
    let pais: String
    let estado: String?
    let departamento: String
    let ciudad: String
    let descripcion: String
    let amenidades: [String]
    let estrellas: Int
    let ranking: Double
    let contactoCelular: String
    let contactoEmail: String
    let imagenes: [String]
    let checkIn: String
    let checkOut: String
    let valorMinimoModificacion: Double
    let usuarioId: String
    let createdAt: String
    let updatedAt: String
    let politicas: [PoliticaDTO]
    let habitaciones: [HabitacionDTO]

    enum CodingKeys: String, CodingKey {
        case id, nombre, direccion, pais, estado, departamento, ciudad
        case descripcion, amenidades, estrellas, ranking, imagenes
        case politicas, habitaciones
        case contactoCelular = "contacto_celular"
        case contactoEmail = "contacto_email"
        case checkIn = "check_in"
        case checkOut = "check_out"
        case valorMinimoModificacion = "valor_minimo_modificacion"
        case usuarioId = "usuario_id"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }

    func toHotel() -> Hotel {
        Hotel(
            id: id,
            nombre: nombre,
            direccion: direccion,
            pais: pais,
            estado: estado,
            departamento: departamento,
            ciudad: ciudad,
            descripcion: descripcion,
            amenidades: amenidades.map({
                HotelAmenity(rawValue: $0) ?? .airConditioning
            }),
            estrellas: estrellas,
            ranking: ranking,
            contactoCelular: contactoCelular,
            contactoEmail: contactoEmail,
            images: imagenes,
            checkInHour: checkIn,
            checkOutHour: checkOut,
            valorMinimoModificacion: valorMinimoModificacion,
            politicas: politicas.map({ $0.toPolitica() }),
            habitaciones: habitaciones.map({ $0.toHabitacion() }),
            precioMinimo: 0
        )
    }
}

/// DTO para una política del hotel
struct PoliticaDTO: Decodable {
    let id: UUID
    let nombre: String
    let descripcion: String?
    let tipo: String
    let penalizacion: Int
    let diasAntelacion: Int

    enum CodingKeys: String, CodingKey {
        case id, nombre, descripcion, tipo, penalizacion
        case diasAntelacion = "dias_antelacion"
    }

    func toPolitica() -> Politica {
        return Politica(
            id: id,
            nombre: nombre,
            descripcion: descripcion,
            tipo: tipo,
            penalizacion: penalizacion,
            diasAntelacion: diasAntelacion
        )
    }
}

/// DTO para una habitación del hotel
struct HabitacionDTO: Decodable {
    let id: UUID
    let capacidad: Int
    let numero: String
    let descripcion: String?
    let imagenes: [String]
    let monto: Double
    let impuestos: Double
    let disponible: Bool

    func toHabitacion() -> Habitacion {
        return Habitacion(
            id: id,
            capacidad: capacidad,
            numero: numero,
            descripcion: descripcion,
            imagenes: imagenes,
            monto: monto,
            impuestos: impuestos,
            disponible: disponible
        )
    }
}
