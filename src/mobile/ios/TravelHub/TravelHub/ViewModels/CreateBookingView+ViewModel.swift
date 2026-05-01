//
//  CreateBookingView+ViewModel.swift
//  TravelHub
//
//  Created by Andres Donoso on 18/04/26.
//

import SwiftUI

extension CreateBookingView {
    @Observable
    class ViewModel {
        var bookingService: BookingService = BookingServiceKey
            .defaultValue
        var toastManager: ToastManager = ToastManagerKey.defaultValue

        var isLoading = false

        @MainActor
        func create(
            habitacionId: UUID,
            fechaEntrada: Date,
            fechaSalida: Date,
            numHuespedes: Int
        ) async -> Bool {
            isLoading = true
            defer { isLoading = false }

            let newBooking = NewBooking(
                habitacionID: habitacionId,
                fechaEntrada: fechaEntrada,
                fechaSalida: fechaSalida,
                numHuespedes: numHuespedes,
                pagoID: nil
            )

            do {
                try await bookingService.create(booking: newBooking)

                toastManager.success(
                    String(
                        localized: .CreateBooking
                            .reservationCreatedDescription
                    ),
                    title: String(
                        localized: .CreateBooking.reservationCreatedTitle
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

            let booking = ModifyBooking(
                id: id,
                habitacionID: habitacionId,
                fechaEntrada: fechaEntrada,
                fechaSalida: fechaSalida,
                numHuespedes: numHuespedes,
            )

            do {
                let _ = try await bookingService.modifyBooking(booking: booking)

                toastManager.success(
                    String(
                        localized: .CreateBooking
                            .reservationModifiedDescription
                    ),
                    title: String(
                        localized: .CreateBooking.reservationModifiedTitle
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
