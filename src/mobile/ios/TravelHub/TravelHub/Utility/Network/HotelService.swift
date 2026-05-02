//
//  HotelService.swift
//  TravelHub
//
//  Created by Assistant on 1/04/26.
//

import Foundation

protocol HotelService {
    func getHotels(queryItems: [URLQueryItem]) async throws -> HotelsResponseDTO
    func getHotelDetail(id: UUID) async throws -> HotelDetailDTO
}

final class HotelServiceImpl: HotelService {
    private let httpService: HttpService
    private let tokenStore: TokenStoring

    init(httpService: HttpService, tokenStore: TokenStoring = KeychainTokenStore.shared) {
        self.httpService = httpService
        self.tokenStore = tokenStore
    }

    func getHotels(queryItems: [URLQueryItem] = []) async throws -> HotelsResponseDTO {
        let token = try tokenStore.readToken()
        var components = URLComponents(url: HttpRoutes.hoteles.url, resolvingAgainstBaseURL: false)!
        if !queryItems.isEmpty {
            components.queryItems = queryItems
        }
        return try await httpService.get(url: components.url!, token: token)
    }

    func getHotelDetail(id: UUID) async throws -> HotelDetailDTO {
        let token = try tokenStore.readToken()
        let url = HttpRoutes.hoteles.url.appendingPathComponent(id.uuidString)
        return try await httpService.get(url: url, token: token)
    }
}
