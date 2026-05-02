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

    init(
        httpService: HttpService,
        tokenStore: TokenStoring = KeychainTokenStore.shared
    ) {
        self.httpService = httpService
        self.tokenStore = tokenStore
    }

    func pay(paymentInfo: NewPayment) async throws -> Payment {
        let body = PayRequest(monto: paymentInfo.monto, medioDePago: paymentInfo.medioDePago, debeFallar: false, payloadCifrado: "")
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
