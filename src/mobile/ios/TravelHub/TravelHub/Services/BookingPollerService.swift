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
    private struct KnownBooking {
        let estado: EstadoReserva
        let hotelName: String?
    }

    private var knownStates: [UUID: KnownBooking] = [:]
    private let pollInterval: Duration = .seconds(30)

    /// Call immediately after a new booking is created so its `pendiente`
    /// state is seeded before the hotel can confirm it.
    func refreshNow(bookingService: BookingService) async {
        print("[Poller] Manual refresh triggered")
        do {
            let response = try await bookingService.fetchBookings(estado: "activas")
            for booking in response.reservas where knownStates[booking.id] == nil {
                knownStates[booking.id] = KnownBooking(estado: booking.estado, hotelName: booking.nombreHotel)
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
                    print("[Poller]   id=\(b.id) estado=\(b.estado.rawValue) known=\(knownStates[b.id]?.estado.rawValue ?? "none")")
                }
                let activeIDs = Set(response.reservas.map(\.id))
                checkForChanges(in: response.reservas)
                detectRejections(activeIDs: activeIDs)
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
               previous.estado != booking.estado,
               booking.estado == .confirmada {
                print("[Poller] Status change detected for \(booking.id): \(previous.estado.rawValue) → \(booking.estado.rawValue)")
                scheduleConfirmedNotification(for: booking)
            }
            knownStates[booking.id] = KnownBooking(estado: booking.estado, hotelName: booking.nombreHotel)
        }
    }

    private func detectRejections(activeIDs: Set<UUID>) {
        for (id, known) in knownStates where !activeIDs.contains(id) {
            if known.estado == .pendiente {
                print("[Poller] Rejection detected for \(id)")
                scheduleRejectedNotification(id: id, hotelName: known.hotelName)
            }
            knownStates.removeValue(forKey: id)
        }
    }

    private func scheduleConfirmedNotification(for booking: BookingListItemDTO) {
        let hotelName = booking.nombreHotel ?? String(localized: "defaultHotelName", table: "MyBookings")
        schedule(
            identifier: booking.id.uuidString,
            title: String(localized: "notificationConfirmedTitle", table: "Notifications"),
            body: String(localized: "notificationConfirmedBody \(hotelName)", table: "Notifications")
        )
    }

    private func scheduleRejectedNotification(id: UUID, hotelName: String?) {
        let name = hotelName ?? String(localized: "defaultHotelName", table: "MyBookings")
        schedule(
            identifier: id.uuidString,
            title: String(localized: "notificationRejectedTitle", table: "Notifications"),
            body: String(localized: "notificationRejectedBody \(name)", table: "Notifications")
        )
    }

    private func schedule(identifier: String, title: String, body: String) {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default

        let request = UNNotificationRequest(
            identifier: identifier,
            content: content,
            trigger: UNTimeIntervalNotificationTrigger(timeInterval: 1, repeats: false)
        )
        UNUserNotificationCenter.current().add(request) { error in
            if let error {
                print("[Poller] Failed to schedule notification: \(error)")
            } else {
                print("[Poller] Notification scheduled for \(identifier)")
            }
        }
    }
}
