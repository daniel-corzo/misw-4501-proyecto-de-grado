//
//  AuthDTO.swift
//  TravelHub
//
//  Created by Germán Martínez Solano on 1/04/26.
//

import Foundation

struct LoginRequest: Encodable {
    let email: String
    let password: String
}

struct LoginResponse: Decodable {
    let accessToken: String
    let tokenType: String
    let expiresIn: Int

    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case tokenType = "token_type"
        case expiresIn = "expires_in"
    }
}

struct LogoutResponse: Decodable {
    let message: String
}
