//
//  BookingDetailView+ViewModel.swift
//  TravelHub
//

import SwiftUI

extension BookingDetailView {
    @Observable
    class ViewModel {
        var bookingService: BookingService = BookingServiceKey.defaultValue
        var hotelService: HotelService = HotelServiceKey.defaultValue
        var toastManager: ToastManager = ToastManagerKey.defaultValue

        var booking: BookingDetailDTO?
        var isLoading = true
        var hasError = false
        var errorMessage: String?
        var isCancelling = false
        var didCancel = false
        var hotel: Hotel?

        @MainActor
        func fetchDetail(bookingId: UUID) async {
            isLoading = true
            hasError = false
            errorMessage = nil
            defer { isLoading = false }

            do {
                booking = try await bookingService.fetchBookingDetail(id: bookingId)
            } catch is CancellationError {
                return
            } catch let error as HttpError where error == .invalidCredentials {
                hasError = true
                errorMessage = String(localized: .BookingDetail.errorUnauthorized)
                toastManager.error(
                    String(localized: .BookingDetail.errorUnauthorized)
                )
            } catch {
                hasError = true
                errorMessage = error.localizedDescription
                toastManager.error(error.localizedDescription)
            }
        }

        @MainActor
        func fetchHotelDetail(id: UUID) async {
            do {
                let hotel = try await hotelService.getHotelDetail(id: id)
                self.hotel = hotel.toHotel()
            } catch is CancellationError {
                 return
            } catch {
                toastManager.error(String(localized: .BookingDetail.errorRetrievingHotel))
            }
        }

        @MainActor
        func cancelBooking(bookingId: UUID) async {
            isCancelling = true
            defer { isCancelling = false }

            do {
                _ = try await bookingService.cancelBooking(id: bookingId)
                didCancel = true
                toastManager.success(
                    String(localized: .BookingDetail.cancelSuccess)
                )
            } catch let error as HttpError where error == .invalidCredentials {
                toastManager.error(
                    String(localized: .BookingDetail.errorUnauthorized)
                )
            } catch {
                toastManager.error(error.localizedDescription)
            }
        }
    }
}
