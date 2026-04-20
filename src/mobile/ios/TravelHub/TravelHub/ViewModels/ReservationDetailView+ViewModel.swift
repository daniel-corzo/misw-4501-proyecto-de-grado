//
//  ReservationDetailView+ViewModel.swift
//  TravelHub
//

import SwiftUI

extension ReservationDetailView {
    @Observable
    class ViewModel {
        var reservationService: ReservationService = ReservationServiceKey.defaultValue
        var toastManager: ToastManager = ToastManagerKey.defaultValue

        var reservation: ReservationDetailDTO?
        var isLoading = true
        var hasError = false
        var errorMessage: String?
        var isCancelling = false
        var didCancel = false

        @MainActor
        func fetchDetail(reservationId: UUID) async {
            isLoading = true
            hasError = false
            errorMessage = nil
            defer { isLoading = false }

            do {
                reservation = try await reservationService.fetchReservationDetail(id: reservationId)
            } catch is CancellationError {
                return
            } catch let error as HttpError where error == .invalidCredentials {
                hasError = true
                errorMessage = String(localized: .ReservationDetail.errorUnauthorized)
                toastManager.error(
                    String(localized: .ReservationDetail.errorUnauthorized)
                )
            } catch {
                hasError = true
                errorMessage = error.localizedDescription
                toastManager.error(error.localizedDescription)
            }
        }

        @MainActor
        func cancelReservation(reservationId: UUID) async {
            isCancelling = true
            defer { isCancelling = false }

            do {
                _ = try await reservationService.cancelReservation(id: reservationId)
                didCancel = true
                toastManager.success(
                    String(localized: .ReservationDetail.cancelSuccess)
                )
            } catch let error as HttpError where error == .invalidCredentials {
                toastManager.error(
                    String(localized: .ReservationDetail.errorUnauthorized)
                )
            } catch {
                toastManager.error(error.localizedDescription)
            }
        }
    }
}
