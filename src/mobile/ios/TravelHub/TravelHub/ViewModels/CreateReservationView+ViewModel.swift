//
//  CreateReservationView+ViewModel.swift
//  TravelHub
//
//  Created by Andres Donoso on 18/04/26.
//

import SwiftUI

extension CreateReservationView {
    @Observable
    class ViewModel {
        var reservationService: ReservationService = ReservationServiceKey
            .defaultValue
        var toastManager: ToastManager = ToastManagerKey.defaultValue

        var isLoading = true

        @MainActor
        func create(
            habitacionId: UUID,
            fechaEntrada: Date,
            fechaSalida: Date,
            numHuespedes: Int
        ) async {
            isLoading = true

            let newReservation = NewReservation(
                habitacionID: habitacionId,
                fechaEntrada: fechaEntrada,
                fechaSalida: fechaSalida,
                numHuespedes: numHuespedes,
                pagoID: nil
            )

            do {
                try await reservationService.create(reservation: newReservation)

                toastManager.success(
                    String(
                        localized: .CreateReservation
                            .reservationCreatedDescription
                    ),
                    title: String(
                        localized: .CreateReservation.reservationCreatedTitle
                    )
                )
            } catch is CancellationError {
                return
            } catch {
                toastManager.error(error.localizedDescription)
            }

            isLoading = false
        }
    }
}
