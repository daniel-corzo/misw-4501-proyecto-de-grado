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
        ) async -> Bool {
            isLoading = true
            defer { isLoading = false }

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
                
                return true
            } catch is CancellationError {
                return false
            } catch {
                toastManager.error(error.localizedDescription)
                return false
            }
        }
        
        @MainActor
        func modify(id: UUID, habitacionId: UUID, fechaEntrada: Date, fechaSalida: Date, numHuespedes: Int) async -> Bool {
            isLoading = true
            defer { isLoading = false }
            
            let reservation = ModifyReservation(
                id: id,
                habitacionID: habitacionId,
                fechaEntrada: fechaEntrada,
                fechaSalida: fechaSalida,
                numHuespedes: numHuespedes,
            )
            
            do {
                let _ = try await reservationService.modifyReservation(reservation: reservation)
                
                toastManager.success(
                    String(
                        localized: .CreateReservation
                            .reservationModifiedDescription
                    ),
                    title: String(
                        localized: .CreateReservation.reservationModifiedTitle
                    )
                )
                
                return true
            } catch is CancellationError {
                return false
            } catch {
                toastManager.error(error.localizedDescription)
                return false
            }
        }
    }
}
