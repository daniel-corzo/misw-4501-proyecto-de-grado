//
//  BookingService.swift
//  TravelHub
//
//  Created by Andres Donoso on 18/04/26.
//

import Foundation

protocol BookingService {
    func create(booking: NewBooking) async throws

    func fetchBookings(estado: String) async throws
        -> ListBookingsResponse

    func fetchBookingDetail(id: UUID) async throws -> BookingDetailDTO

    @discardableResult
    func cancelBooking(id: UUID) async throws -> BookingListItemDTO

    func modifyBooking(booking: ModifyBooking) async throws
        -> ModifyBookingResponse
}

final class BookingServiceImpl: BookingService {
    private let httpService: HttpService
    private let tokenStore: TokenStoring

    init(
        httpService: HttpService,
        tokenStore: TokenStoring = KeychainTokenStore.shared
    ) {
        self.httpService = httpService
        self.tokenStore = tokenStore
    }

    func create(booking: NewBooking) async throws {
        let body = CreateBookingRequest(
            habitacionID: booking.habitacionID,
            fechaEntrada: booking.fechaEntrada.ISO8601Format(
                .iso8601.year().month().day()
            ),
            fechaSalida: booking.fechaSalida.ISO8601Format(
                .iso8601.year().month().day()
            ),
            numHuespedes: booking.numHuespedes
        )
        let token = try tokenStore.readToken() ?? ""

        let _: CreateBookingResponse = try await httpService.post(
            url: HttpRoutes.reservas().url,
            body: body,
            token: token
        )
    }

    func fetchBookings(estado: String) async throws
        -> ListBookingsResponse
    {
        let token = try tokenStore.readToken() ?? ""
        var components = URLComponents(
            url: HttpRoutes.reservas().url,
            resolvingAgainstBaseURL: false
        )!
        components.queryItems = [URLQueryItem(name: "estado", value: estado)]
        let url = components.url!

        return try await httpService.get(url: url, token: token)
    }

    func fetchBookingDetail(id: UUID) async throws -> BookingDetailDTO {
        let token = try tokenStore.readToken() ?? ""
        let url = HttpRoutes.reservas().url.appendingPathComponent(
            id.uuidString
        )
        return try await httpService.get(url: url, token: token)
    }

    @discardableResult
    func cancelBooking(id: UUID) async throws -> BookingListItemDTO {
        let token = try tokenStore.readToken() ?? ""
        let url = HttpRoutes.reservas().url
            .appendingPathComponent(id.uuidString)
            .appendingPathComponent("cancelar")
        return try await httpService.patch(url: url, token: token)
    }

    func modifyBooking(booking: ModifyBooking) async throws
        -> ModifyBookingResponse
    {
        let token = try tokenStore.readToken() ?? ""
        let url = HttpRoutes.reservas(id: booking.id).url

        let body = ModifyBookingRequest(
            fechaEntrada: booking.fechaEntrada.ISO8601Format(
                .iso8601.year().month().day()
            ),
            fechaSalida: booking.fechaSalida.ISO8601Format(
                .iso8601.year().month().day()
            ),
            numHuespedes: booking.numHuespedes,
            habitacionId: booking.habitacionID
        )

        return try await httpService.patch(url: url, token: token, body: body)
    }
}
