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
    let estado: String
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
    let habitaciones: [HabitacionDTO]

    enum CodingKeys: String, CodingKey {
        case id, nombre, direccion, pais, estado, departamento, ciudad
        case descripcion, amenidades, estrellas, ranking, imagenes, habitaciones
        case contactoCelular = "contacto_celular"
        case contactoEmail = "contacto_email"
        case checkIn = "check_in"
        case checkOut = "check_out"
        case valorMinimoModificacion = "valor_minimo_modificacion"
    }
}

/// DTO para una habitación del hotel
struct HabitacionDTO: Decodable {
    let id: UUID
    let capacidad: Int
    let numero: Int
    let descripcion: String
    let imagenes: [String]
    let monto: Double
    let impuestos: Double
    let disponible: Bool
}
