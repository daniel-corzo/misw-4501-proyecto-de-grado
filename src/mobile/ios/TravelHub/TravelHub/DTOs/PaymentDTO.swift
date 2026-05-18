//
//  PaymentDTO.swift
//  TravelHub
//
//  Created by Andres Donoso on 2/05/26.
//

import Foundation

struct PayRequest: Encodable {
    var monto: Int
    var medioDePago: String
    var debeFallar: Bool
    var numero: String
    var cvv: String
    var fechaExpiracion: String

    enum CodingKeys: String, CodingKey {
        case monto
        case medioDePago = "medio_de_pago"
        case debeFallar = "debe_fallar"
        case numero
        case cvv
        case fechaExpiracion = "fecha_expiracion"
    }
}

struct PayResponse: Decodable {
    var id: UUID
    var monto: Int
    var medioDePago: String
    var estado: PaymentState
    var tarjetaUltimos4: String?

    enum CodingKeys: String, CodingKey {
        case id
        case monto
        case estado
        case medioDePago = "medio_de_pago"
        case tarjetaUltimos4 = "tarjeta_ultimos_4"
    }
}
