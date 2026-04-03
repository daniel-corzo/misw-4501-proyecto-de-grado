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

        func fetchHotels(toastManager: ToastManager) {
            Task { [weak self] in
                guard let self else { return }
                
                do {
                    let response: HotelsResponseDTO = try await hotelService.getHotels()
                    let mapped = response.hoteles.map { $0.toDomain() }
                    await MainActor.run {
                        self.hotels = mapped
                    }
                } catch {
                    await MainActor.run {
                        toastManager.error("Error")
                    }
                }
            }
        }
    }
}
private extension HotelDTO {
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
            ranking: estrellas,
            contactoCelular: "",
            contactoEmail: "",
            images: imagenes,
            checkInHour: "",
            checkOutHour: "",
            valorMinimoModificacion: precioMinimo
        )
    }
}

