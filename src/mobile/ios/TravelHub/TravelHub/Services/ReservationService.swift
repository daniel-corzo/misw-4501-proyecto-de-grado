//
//  ReservationService.swift
//  TravelHub
//
//  Created by Andres Donoso on 18/04/26.
//

import Foundation

protocol ReservationService {
    func create(reservation: NewReservation) async throws
    func fetchReservations(estado: String) async throws -> ListReservationsResponse
}

final class ReservationServiceImpl: ReservationService {
    private let httpService: HttpService
    private let tokenStore: TokenStoring

    init(
        httpService: HttpService,
        tokenStore: TokenStoring = KeychainTokenStore.shared
    ) {
        self.httpService = httpService
        self.tokenStore = tokenStore
    }

    func create(reservation: NewReservation) async throws {
        let body = CreateReservationRequest(
            habitacionID: reservation.habitacionID,
            fechaEntrada: reservation.fechaEntrada.ISO8601Format(.iso8601.year().month().day()),
            fechaSalida: reservation.fechaSalida.ISO8601Format(.iso8601.year().month().day()),
            numHuespedes: reservation.numHuespedes
        )
        let token = try tokenStore.readToken() ?? ""

        let _: CreateReservationResponse = try await httpService.post(
            url: HttpRoutes.reservas.url,
            body: body,
            token: token
        )
    }

    func fetchReservations(estado: String) async throws -> ListReservationsResponse {
        let token = try tokenStore.readToken() ?? ""
        var components = URLComponents(url: HttpRoutes.reservas.url, resolvingAgainstBaseURL: false)!
        components.queryItems = [URLQueryItem(name: "estado", value: estado)]
        let url = components.url!

        return try await httpService.get(url: url, token: token)
    }
}
