//
//  HotelDetailView+ViewModel.swift
//  TravelHub
//
//  Created by Andres Donoso on 23/03/26.
//

import Foundation

extension HotelDetailView {
    @Observable
    class ViewModel {
        var hotel: Hotel?
        var isLoading = true
        var hotelService: HotelService = HotelServiceKey.defaultValue

        @MainActor
        func fetchHotelDetail(hotelId: UUID, toastManager: ToastManager) async {
            isLoading = true

            do {
                let response = try await hotelService.getHotelDetail(id: hotelId)
                hotel = response.toDomain()
            } catch is CancellationError {
                return
            } catch {
                toastManager.error(error.localizedDescription)
            }

            isLoading = false
        }
    }
}

private extension HotelDetailDTO {
    func toDomain() -> Hotel {
        return Hotel(
            id: id,
            nombre: nombre,
            direccion: direccion,
            pais: pais,
            estado: estado,
            departamento: departamento,
            ciudad: ciudad,
            descripcion: descripcion,
            amenidades: amenidades.compactMap { HotelAmenity(rawValue: $0) },
            estrellas: estrellas,
            ranking: ranking,
            contactoCelular: contactoCelular,
            contactoEmail: contactoEmail,
            images: imagenes,
            checkInHour: checkIn,
            checkOutHour: checkOut,
            valorMinimoModificacion: valorMinimoModificacion,
            habitaciones: habitaciones.map { $0.toDomain() }
        )
    }
}

private extension HabitacionDTO {
    func toDomain() -> Habitacion {
        return Habitacion(
            id: id,
            capacidad: capacidad,
            numero: numero,
            descripcion: descripcion,
            imagenes: imagenes,
            monto: monto,
            impuestos: impuestos,
            disponible: disponible
        )
    }
}
