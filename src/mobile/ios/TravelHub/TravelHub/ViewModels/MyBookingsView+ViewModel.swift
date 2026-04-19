//
//  MyBookingsView+ViewModel.swift
//  TravelHub
//

import SwiftUI

// MARK: - Booking Tab

enum BookingTab: Int, CaseIterable {
    case active
    case past
    case cancelled

    var estadoQuery: String {
        switch self {
        case .active: return "activas"
        case .past: return "pasadas"
        case .cancelled: return "canceladas"
        }
    }

    var title: LocalizedStringResource {
        switch self {
        case .active: return .MyBookings.tabActive
        case .past: return .MyBookings.tabPast
        case .cancelled: return .MyBookings.tabCancelled
        }
    }

    var sectionTitle: LocalizedStringResource {
        switch self {
        case .active: return .MyBookings.sectionActive
        case .past: return .MyBookings.sectionPast
        case .cancelled: return .MyBookings.sectionCancelled
        }
    }

    var emptyMessage: LocalizedStringResource {
        switch self {
        case .active: return .MyBookings.emptyActive
        case .past: return .MyBookings.emptyPast
        case .cancelled: return .MyBookings.emptyCancelled
        }
    }

    func bookingCountMessage(_ count: Int) -> LocalizedStringResource {
        switch self {
        case .active: return .MyBookings.bookingCountActive(count)
        case .past: return .MyBookings.bookingCountPast(count)
        case .cancelled: return .MyBookings.bookingCountCancelled(count)
        }
    }
}

// MARK: - Badge Display

extension EstadoReserva {
    var badgeLabel: String {
        switch self {
        case .confirmada: return "CONFIRMED"
        case .pendiente: return "UPCOMING"
        case .cancelada: return "CANCELLED"
        case .completada: return "COMPLETED"
        }
    }

    var badgeColor: Color {
        switch self {
        case .confirmada: return .green
        case .pendiente: return .orange
        case .cancelada: return .red
        case .completada: return .blue
        }
    }
}

// MARK: - ViewModel

extension MyBookingsView {
    @Observable
    class ViewModel {
        var reservationService: ReservationService = ReservationServiceKey.defaultValue
        var toastManager: ToastManager = ToastManagerKey.defaultValue

        var selectedTab: BookingTab = .active
        var reservations: [ReservationListItemDTO] = []
        var isLoading = false
        var hasError = false

        @MainActor
        func fetchReservations() async {
            isLoading = true
            hasError = false

            do {
                let response = try await reservationService.fetchReservations(
                    estado: selectedTab.estadoQuery
                )
                reservations = response.reservas
            } catch is CancellationError {
                return
            } catch let error as HttpError where error == .invalidCredentials {
                hasError = true
                toastManager.error(
                    String(localized: .MyBookings.errorUnauthorized)
                )
            } catch {
                hasError = true
                toastManager.error(error.localizedDescription)
            }

            isLoading = false
        }
    }
}
