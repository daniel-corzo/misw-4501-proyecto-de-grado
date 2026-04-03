import Foundation

/// Respuesta para el listado de hoteles
struct HotelsResponseDTO: Decodable {
    let total: Int
    let hoteles: [HotelDTO]
}

/// DTO que representa un hotel según la respuesta del backend
struct HotelDTO: Decodable {
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
