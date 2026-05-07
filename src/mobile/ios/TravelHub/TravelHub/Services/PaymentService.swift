//
//  PaymentService.swift
//  TravelHub
//
//  Created by Andres Donoso on 2/05/26.
//

import Foundation

protocol PaymentService {
    func pay(paymentInfo: NewPayment) async throws -> Payment
}

final class PaymentServiceImpl: PaymentService {
    private let httpService: HttpService
    private let tokenStore: TokenStoring
    private let cipher: PaymentPayloadEncrypting

    init(
        httpService: HttpService,
        tokenStore: TokenStoring = KeychainTokenStore.shared,
        cipher: PaymentPayloadEncrypting
    ) {
        self.httpService = httpService
        self.tokenStore = tokenStore
        self.cipher = cipher
    }

    func pay(paymentInfo: NewPayment) async throws -> Payment {
        let numero = PaymentPayloadNormalization.normalizedPAN(paymentInfo.creditCardNumber)
        let fecha = PaymentPayloadNormalization.normalizedExpiry(paymentInfo.expirationDate)
        let cvv = paymentInfo.cvv.trimmingCharacters(in: .whitespacesAndNewlines)

        let payloadCifrado = try cipher.encryptCardPayload(
            numero: numero,
            cvv: cvv,
            fechaExpiracion: fecha
        )

        let body = PayRequest(
            monto: paymentInfo.monto,
            medioDePago: paymentInfo.medioDePago,
            debeFallar: false,
            payloadCifrado: payloadCifrado
        )
        let token = try tokenStore.readToken() ?? ""

        let response: PayResponse = try await httpService.post(
            url: HttpRoutes.pagar.url,
            body: body,
            token: token
        )

        return Payment(
            id: response.id,
            monto: response.monto,
            medioDePago: response.medioDePago,
            estado: response.estado,
            tarjetaUltimos4: response.tarjetaUltimos4
        )
    }
}
