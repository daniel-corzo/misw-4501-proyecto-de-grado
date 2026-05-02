//
//  ListHotel+ViewModel.swift
//  TravelHub
//
//  Created by Germán Martínez Solano on 23/03/26.
//

import Foundation
import SwiftUI

enum HotelSortOrder: CaseIterable, Identifiable {
    case recommended
    case priceLowToHigh
    case priceHighToLow
    case ratingHighToLow

    var id: Self { self }

    var queryValue: String {
        switch self {
        case .recommended, .ratingHighToLow: return "rating_desc"
        case .priceLowToHigh: return "precio_asc"
        case .priceHighToLow: return "precio_desc"
        }
    }

    var localizedName: LocalizedStringResource {
        switch self {
        case .recommended: return .HotelList.recommended
        case .priceLowToHigh: return .HotelList.priceLowToHigh
        case .priceHighToLow: return .HotelList.priceHighToLow
        case .ratingHighToLow: return .HotelList.ratingHighToLow
        }
    }
}

extension ListHotelView {
    @Observable
    class ViewModel {
        var hotels: [Hotel] = []
        var totalCount: Int = 0
        var hotelService: HotelService = HotelServiceKey.defaultValue

        // Filter state
        var sortOrder: HotelSortOrder = .recommended
        var priceLow: Double = 0
        var priceHigh: Double = 1_000_000
        var selectedStars: Set<Int> = []
        var selectedAmenities: Set<HotelAmenity> = []

        var hasActiveFilters: Bool {
            sortOrder != .recommended ||
            priceLow > 0 ||
            priceHigh < 1_000_000 ||
            !selectedStars.isEmpty ||
            !selectedAmenities.isEmpty
        }

        func resetFilters() {
            sortOrder = .recommended
            priceLow = 0
            priceHigh = 1_000_000
            selectedStars = []
            selectedAmenities = []
        }

        func buildQueryItems() -> [URLQueryItem] {
            var items: [URLQueryItem] = []
            items.append(URLQueryItem(name: "orden", value: sortOrder.queryValue))
            items.append(URLQueryItem(name: "limit", value: "100"))

            if priceLow > 0 {
                items.append(URLQueryItem(name: "precio_min", value: String(Int(priceLow))))
            }
            if priceHigh < 1_000_000 {
                items.append(URLQueryItem(name: "precio_max", value: String(Int(priceHigh))))
            }
            for star in selectedStars.sorted() {
                items.append(URLQueryItem(name: "estrellas", value: String(star)))
            }
            for amenity in selectedAmenities {
                items.append(URLQueryItem(name: "amenidades_populares", value: amenity.rawValue))
            }

            return items
        }

        @MainActor
        func fetchHotels(toastManager: ToastManager) async {
            do {
                let queryItems = buildQueryItems()
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
