//
//  HotelService.swift
//  TravelHub
//
//  Created by Assistant on 1/04/26.
//

import Foundation

protocol HotelService {
    /// Obtiene la lista de hoteles desde el backend
    func getHotels() async throws -> HotelsResponseDTO

    /// Obtiene el detalle de un hotel por su ID
    func getHotelDetail(id: UUID) async throws -> HotelDetailDTO
}

final class HotelServiceImpl: HotelService {
    private let httpService: HttpService
    private let tokenStore: TokenStoring

    init(httpService: HttpService, tokenStore: TokenStoring = KeychainTokenStore.shared) {
        self.httpService = httpService
        self.tokenStore = tokenStore
    }

    func getHotels() async throws -> HotelsResponseDTO {
        let token = try tokenStore.readToken()
        return try await httpService.get(url: HttpRoutes.hoteles.url, token: token)
    }

    func getHotelDetail(id: UUID) async throws -> HotelDetailDTO {
        let token = try tokenStore.readToken()
        let url = HttpRoutes.hoteles.url.appendingPathComponent(id.uuidString)
        return try await httpService.get(url: url, token: token)
    }
}
