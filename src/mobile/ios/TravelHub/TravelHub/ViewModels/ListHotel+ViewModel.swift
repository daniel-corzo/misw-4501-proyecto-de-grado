//
//  ListHotel+ViewModel.swift
//  TravelHub
//
//  Created by Germán Martínez Solano on 23/03/26.
//

import Foundation
import SwiftUI

enum HotelSortOrder: CaseIterable, Identifiable {
    case priceLowToHigh
    case priceHighToLow
    case ratingHighToLow

    var id: Self { self }

    var queryValue: String {
        switch self {
        case .ratingHighToLow: return "rating_desc"
        case .priceLowToHigh: return "precio_asc"
        case .priceHighToLow: return "precio_desc"
        }
    }

    var localizedName: LocalizedStringResource {
        switch self {
        case .priceLowToHigh: return .HotelList.priceLowToHigh
        case .priceHighToLow: return .HotelList.priceHighToLow
        case .ratingHighToLow: return .HotelList.ratingHighToLow
        }
    }
}

extension ListHotelView {
    @Observable
    class ViewModel {
        static let defaultSortOrder: HotelSortOrder = .ratingHighToLow
        static let defaultPriceLow: Double = 0
        static let defaultPriceHigh: Double = 1_000_000
        static let pageSize = 20

        var hotels: [Hotel] = []
        var totalCount: Int = 0
        var isLoadingMore: Bool = false
        var hotelService: HotelService = HotelServiceKey.defaultValue

        var sortOrder: HotelSortOrder = defaultSortOrder
        var priceLow: Double = defaultPriceLow
        var priceHigh: Double = defaultPriceHigh
        var selectedStars: Set<Int> = []
        var selectedAmenities: Set<HotelAmenity> = []

        var hasMorePages: Bool {
            hotels.count < totalCount
        }

        var hasActiveFilters: Bool {
            sortOrder != Self.defaultSortOrder ||
            priceLow > Self.defaultPriceLow ||
            priceHigh < Self.defaultPriceHigh ||
            !selectedStars.isEmpty ||
            !selectedAmenities.isEmpty
        }

        func resetFilters() {
            sortOrder = Self.defaultSortOrder
            priceLow = Self.defaultPriceLow
            priceHigh = Self.defaultPriceHigh
            selectedStars = []
            selectedAmenities = []
        }

        func buildQueryItems(offset: Int) -> [URLQueryItem] {
            var items: [URLQueryItem] = []
            items.append(URLQueryItem(name: "orden", value: sortOrder.queryValue))
            items.append(URLQueryItem(name: "limit", value: String(Self.pageSize)))
            items.append(URLQueryItem(name: "offset", value: String(offset)))

            if priceLow > Self.defaultPriceLow {
                items.append(URLQueryItem(name: "precio_min", value: String(Int(priceLow))))
            }
            if priceHigh < Self.defaultPriceHigh {
                items.append(URLQueryItem(name: "precio_max", value: String(Int(priceHigh))))
            }
            for star in selectedStars.sorted() {
                items.append(URLQueryItem(name: "estrellas", value: String(star)))
            }
            for amenity in selectedAmenities.sorted(by: { $0.rawValue < $1.rawValue }) {
                items.append(URLQueryItem(name: "amenidades_populares", value: amenity.rawValue))
            }

            return items
        }

        @MainActor
        func fetchHotels(toastManager: ToastManager) async {
            do {
                let queryItems = buildQueryItems(offset: 0)
                let response: HotelsResponseDTO = try await hotelService.getHotels(queryItems: queryItems)
                hotels = response.hoteles.map { $0.toDomain() }
                totalCount = response.total
            } catch is CancellationError {
                return
            } catch {
                toastManager.error(error.localizedDescription)
            }
        }

        @MainActor
        func loadMoreIfNeeded(currentHotel: Hotel, toastManager: ToastManager) async {
            guard !isLoadingMore, hasMorePages else { return }

            let thresholdIndex = max(hotels.count - 5, 0)
            guard let index = hotels.firstIndex(where: { $0.id == currentHotel.id }),
                  index >= thresholdIndex else { return }

            isLoadingMore = true
            do {
                let queryItems = buildQueryItems(offset: hotels.count)
                let response: HotelsResponseDTO = try await hotelService.getHotels(queryItems: queryItems)
                hotels.append(contentsOf: response.hoteles.map { $0.toDomain() })
                totalCount = response.total
            } catch is CancellationError {
                // no-op
            } catch {
                toastManager.error(error.localizedDescription)
            }
            isLoadingMore = false
        }

        @MainActor
        func fetchHotelDetail(hotelId: UUID, toastManager: ToastManager) async -> Hotel? {
            do {
                return try await hotelService.getHotelDetail(id: hotelId).toHotel()
            } catch is CancellationError {
                return nil
            } catch {
                toastManager.error(error.localizedDescription)
            }

            return nil
        }
    }
}

private extension HotelListDTO {
    func toDomain() -> Hotel {
        return Hotel(
            id: id,
            nombre: nombre,
            direccion: "",
            pais: pais,
            estado: "",
            departamento: "",
            ciudad: ciudad,
            descripcion: "",
            amenidades: amenidades.compactMap { HotelAmenity(rawValue: $0) },
            estrellas: estrellas,
            ranking: 0,
            contactoCelular: "",
            contactoEmail: "",
            images: imagenes,
            checkInHour: "",
            checkOutHour: "",
            valorMinimoModificacion: 0,
            politicas: [],
            habitaciones: [],
            precioMinimo: precioMinimo
        )
    }
}
