//
//  Payment.swift
//  TravelHub
//
//  Created by Andres Donoso on 2/05/26.
//

import Foundation

enum PaymentState: String, Codable {
    case successful = "successful"
    case failed = "failed"
}

struct Payment {
    var id: UUID
    var monto: Int
    var medioDePago: String
    var estado: PaymentState
    var tarjetaUltimos4: String?
}

struct NewPayment {
    var monto: Int
    var medioDePago: String
    var creditCardNumber: String
    var cardholderName: String
    var cvv: String
    var expirationDate: String
}
