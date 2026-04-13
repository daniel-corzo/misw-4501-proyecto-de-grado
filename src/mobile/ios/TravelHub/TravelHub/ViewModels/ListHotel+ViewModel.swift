//
//  ListHotel+ViewModel.swift
//  TravelHub
//
//  Created by Germán Martínez Solano on 23/03/26.
//

import Foundation
import Combine
import SwiftUI

extension ListHotelView {
    @Observable
    class ViewModel {
        var hotels: [Hotel] = []
        var hotelService: HotelService = HotelServiceKey.defaultValue
        
        @MainActor
        func fetchHotels(toastManager: ToastManager) async {
            do {
                let response: HotelsResponseDTO = try await hotelService.getHotels()
                hotels = response.hoteles.map { $0.toDomain() }
            } catch is CancellationError {
                return
            } catch {
                toastManager.error(error.localizedDescription)
            }
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
            amenidades: [],
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

