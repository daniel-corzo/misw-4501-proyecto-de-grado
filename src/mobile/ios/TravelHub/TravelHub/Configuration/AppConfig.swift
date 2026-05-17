//
//  AppConfig.swift
//  TravelHub
//
//  Created by Andres Donoso on 29/03/26.
//

import Foundation

enum AppConfig {
    static var baseURL: URL {
        guard let urlString = Bundle.main.object(forInfoDictionaryKey: "BASE_URL") as? String,
              let url = URL(string: urlString) else {
            fatalError("BASE_URL not set in Info.plist")
        }

        return url
    }

    /// PEM for RSA-OAEP payment payload; prefers ``payment_public.pem``, then ``payment_public.example.pem``.
    static var paymentPublicKeyPEM: String {
        for name in ["payment_public", "payment_public.example"] {
            guard let url = Bundle.main.url(forResource: name, withExtension: "pem"),
                  let pem = try? String(contentsOf: url, encoding: .utf8),
                  pem.contains("BEGIN PUBLIC KEY")
            else { continue }
            return pem
        }

        fatalError(
            "Missing payment RSA public key: add Resources/payment_public.pem (copy from payment_public.example.pem and match PAGO_RSA_PRIVATE_KEY_PEM)."
        )
    }
}
