//
//  BookingCardView.swift
//  TravelHub
//

import SwiftUI

struct BookingCardView: View {
    let reservation: ReservationListItemDTO

    private var hotelName: String {
        reservation.nombreHotel ?? String(localized: .MyBookings.defaultHotelName)
    }

    private var roomName: String {
        reservation.nombreHabitacion ?? String(localized: .MyBookings.defaultRoomName)
    }

    private static let inputFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        return f
    }()

    private static let displayFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateFormat = "MMM dd"
        return f
    }()

    private static let yearFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateFormat = "yyyy"
        return f
    }()

    private var dateRangeText: String {
        guard let start = Self.inputFormatter.date(from: reservation.fechaEntrada),
              let end = Self.inputFormatter.date(from: reservation.fechaSalida) else {
            return "\(reservation.fechaEntrada) - \(reservation.fechaSalida)"
        }

        let startStr = Self.displayFormatter.string(from: start)
        let endStr = Self.displayFormatter.string(from: end)
        let year = Self.yearFormatter.string(from: end)

        return "\(startStr) - \(endStr), \(year)"
    }

    private var guestsText: String {
        String(localized: .MyBookings.guests(reservation.numHuespedes))
    }

    var body: some View {
        VStack(spacing: 0) {
            // MARK: - Image with badge
            ZStack(alignment: .topTrailing) {
                AsyncImage(url: reservation.imagenesHotel.first.flatMap { URL(string: $0) }) { phase in
                    switch phase {
                    case .success(let image):
                        Color.clear
                            .frame(maxWidth: .infinity)
                            .frame(height: 180)
                            .overlay {
                                image
                                    .resizable()
                                    .scaledToFill()
                            }
                            .clipped()
                    default:
                        ZStack {
                            Color.gray.opacity(0.15)
                            Image(systemName: "building.2")
                                .resizable()
                                .scaledToFit()
                                .foregroundStyle(.gray.opacity(0.4))
                                .padding(50)
                        }
                        .frame(height: 180)
                        .frame(maxWidth: .infinity)
                    }
                }

                // Badge
                Text(reservation.estado.badgeLabel)
                    .font(.caption2)
                    .fontWeight(.bold)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 5)
                    .background(reservation.estado.badgeColor.opacity(0.9))
                    .foregroundStyle(.white)
                    .clipShape(Capsule())
                    .padding(12)
            }

            // MARK: - Content
            VStack(alignment: .leading, spacing: 8) {
                Text(hotelName)
                    .font(.title3)
                    .fontWeight(.bold)
                    .lineLimit(1)

                HStack(spacing: 6) {
                    Image(systemName: "calendar")
                        .foregroundStyle(.gray)
                        .font(.footnote)
                    Text(dateRangeText)
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }

                HStack(spacing: 6) {
                    Image(systemName: "person.2")
                        .foregroundStyle(.gray)
                        .font(.footnote)
                    Text("\(guestsText), 1 \(roomName)")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }

                // View Details button
                NavigationLink {
                    // Placeholder for reservation detail
                    Text("Reservation \(reservation.id.uuidString)")
                        .navigationTitle(hotelName)
                } label: {
                    Text(LocalizedStringResource.MyBookings.viewDetails)
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundStyle(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                        .background(Color.blue)
                        .clipShape(Capsule())
                }
                .padding(.top, 4)
            }
            .padding(16)
        }
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 20))
        .shadow(color: .black.opacity(0.1), radius: 10, y: 5)
    }
}

#Preview {
    NavigationStack {
        BookingCardView(
            reservation: ReservationListItemDTO(
                id: UUID(),
                habitacionId: UUID(),
                nombreHabitacion: "Deluxe Room",
                nombreHotel: "Grand Hyatt Regency",
                imagenesHotel: ["https://raw.githubusercontent.com/DavidMS73/images-test/main/hotel1.jpeg"],
                fechaEntrada: "2023-10-24",
                fechaSalida: "2023-10-27",
                numHuespedes: 2,
                estado: .confirmada,
                pagoId: nil,
                createdAt: "2023-10-20T10:00:00Z"
            )
        )
        .padding()
    }
}
