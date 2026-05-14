//
//  BookingPollerService.swift
//  TravelHub
//

import Foundation
import UserNotifications

// Allows notification banners to appear even while the app is in the foreground.
final class NotificationDelegate: NSObject, UNUserNotificationCenterDelegate {
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        completionHandler([.banner, .sound])
    }
}

final class BookingPollerService {
    private var knownStates: [UUID: EstadoReserva] = [:]
    private let pollInterval: Duration = .seconds(30)

    /// Call immediately after a new booking is created so its `pendiente`
    /// state is seeded before the hotel can confirm it.
    func refreshNow(bookingService: BookingService) async {
        print("[Poller] Manual refresh triggered")
        do {
            let response = try await bookingService.fetchBookings(estado: "activas")
            for booking in response.reservas where knownStates[booking.id] == nil {
                knownStates[booking.id] = booking.estado
                print("[Poller] Seeded \(booking.id) as \(booking.estado.rawValue)")
            }
        } catch {
            print("[Poller] Manual refresh error: \(error)")
        }
    }

    func start(bookingService: BookingService) async {
        print("[Poller] Started")
        while !Task.isCancelled {
            print("[Poller] Fetching active bookings…")
            do {
                let response = try await bookingService.fetchBookings(estado: "activas")
                print("[Poller] Got \(response.reservas.count) booking(s)")
                for b in response.reservas {
                    print("[Poller]   id=\(b.id) estado=\(b.estado.rawValue) known=\(knownStates[b.id]?.rawValue ?? "none")")
                }
                checkForChanges(in: response.reservas)
            } catch {
                print("[Poller] Fetch error: \(error)")
            }
            print("[Poller] Sleeping \(pollInterval)…")
            try? await Task.sleep(for: pollInterval)
        }
        print("[Poller] Cancelled")
    }

    private func checkForChanges(in bookings: [BookingListItemDTO]) {
        for booking in bookings {
            if let previous = knownStates[booking.id],
               previous != booking.estado,
               booking.estado == .confirmada {
                print("[Poller] Status change detected for \(booking.id): \(previous.rawValue) → \(booking.estado.rawValue)")
                scheduleNotification(for: booking)
            }
            knownStates[booking.id] = booking.estado
        }
    }

    private func scheduleNotification(for booking: BookingListItemDTO) {
        let content = UNMutableNotificationContent()
        let hotelName = booking.nombreHotel ?? String(localized: "defaultHotelName", table: "MyBookings")
        content.title = String(localized: "notificationConfirmedTitle", table: "Notifications")
        content.body = String(localized: "notificationConfirmedBody \(hotelName)", table: "Notifications")
        content.sound = .default

        let request = UNNotificationRequest(
            identifier: booking.id.uuidString,
            content: content,
            trigger: UNTimeIntervalNotificationTrigger(timeInterval: 1, repeats: false)
        )
        UNUserNotificationCenter.current().add(request) { error in
            if let error {
                print("[Poller] Failed to schedule notification: \(error)")
            } else {
                print("[Poller] Notification scheduled for \(booking.id)")
            }
        }
    }
}
