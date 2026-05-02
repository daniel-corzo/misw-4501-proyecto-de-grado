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
    var payloadCifrado: String
    
    enum CodingKeys: String, CodingKey {
        case monto
        case medioDePago = "medio_de_pago"
        case debeFallar = "debe_fallar"
        case payloadCifrado = "payload_cifrado"
    }
}

struct PayResponse: Decodable {
    var id: UUID
    var monto: Int
    var medioDePago: String
    var estado: PaymentState
    var tarjetaUltimos4: String?
}
