//
//  BookingDetailView.swift
//  TravelHub
//

import SwiftUI

struct BookingDetailView: View {
    let bookingId: UUID

    @Environment(\.bookingService) private var bookingService
    @Environment(\.hotelService) private var hotelService
    @Environment(\.toastManager) private var toastManager
    @Environment(\.dismiss) private var dismiss

    @State private var viewModel = ViewModel()
    @State private var showCancelConfirmation = false

    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView()
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if viewModel.hasError {
                errorView
            } else if let booking = viewModel.booking {
                successView(booking)
            }
        }
        .navigationTitle(LocalizedStringResource.BookingDetail.navigationTitle)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar(.hidden, for: .tabBar)
        .task {
            viewModel.bookingService = bookingService
            viewModel.toastManager = toastManager
            viewModel.hotelService = hotelService
            await viewModel.fetchDetail(bookingId: bookingId)

            if let booking = self.viewModel.booking, let hotelId = booking.hotel.id {
                await viewModel.fetchHotelDetail(id: hotelId)
            }
        }
        .refreshable {
            await viewModel.fetchDetail(bookingId: bookingId)
        }
        .onChange(of: viewModel.didCancel) { _, didCancel in
            if didCancel {
                dismiss()
            }
        }
    }

    // MARK: - Success Content

    private func successView(_ booking: BookingDetailDTO) -> some View {
        VStack(spacing: 0) {
            ScrollView {
                VStack(spacing: 20) {
                    statusCard(booking)
                    hotelCard(booking)
                    datesCard(booking)
                    roomCard(booking)
                    qrCodeCard
                    contactCard(booking)
                }
                .padding(.horizontal, 20)
                .padding(.top, 16)
                .padding(.bottom, 24)
            }

            if booking.estado == .confirmada || booking.estado == .pendiente {
                footerButtons
            }
        }
    }

    // MARK: - Status Card

    private func statusCard(_ booking: BookingDetailDTO) -> some View {
        VStack(spacing: 12) {
            Image(systemName: booking.estado.detailIcon)
                .resizable()
                .scaledToFit()
                .frame(width: 48, height: 48)
                .foregroundStyle(booking.estado.badgeColor)

            Text(booking.estado.badgeLabel)
                .font(.headline)
                .fontWeight(.bold)
                .foregroundStyle(booking.estado.badgeColor)

            Text(
                String(
                    localized: .BookingDetail.bookingId(
                        booking.codigoReserva
                    )
                )
            )
            .font(.subheadline)
            .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 20)
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .shadow(color: .black.opacity(0.07), radius: 8, y: 2)
    }

    // MARK: - Hotel Card

    private func hotelCard(_ booking: BookingDetailDTO) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            // Hotel image
            AsyncImage(url: booking.hotel.imagenes.first.flatMap { URL(string: $0) }) { phase in
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
            .clipShape(
                UnevenRoundedRectangle(
                    topLeadingRadius: 16,
                    bottomLeadingRadius: 0,
                    bottomTrailingRadius: 0,
                    topTrailingRadius: 16
                )
            )

            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text(booking.hotel.nombre)
                        .font(.title3)
                        .fontWeight(.bold)

                    Spacer()

                    if let stars = booking.hotel.estrellas {
                        HStack(spacing: 2) {
                            Text("\(stars)")
                                .font(.subheadline)
                                .fontWeight(.semibold)
                            Image(systemName: "star.fill")
                                .font(.caption)
                        }
                        .foregroundStyle(.accent)
                    }
                }

                if let address = booking.hotel.direccion {
                    HStack(spacing: 4) {
                        Image(systemName: "mappin.and.ellipse")
                            .font(.caption)
                        Text(hotelLocationText(booking.hotel, address: address))
                            .font(.subheadline)
                    }
                    .foregroundStyle(.secondary)
                }
            }
            .padding(.horizontal, 16)
            .padding(.bottom, 16)
        }
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .shadow(color: .black.opacity(0.07), radius: 8, y: 2)
    }

    // MARK: - Dates Card

    private func datesCard(_ booking: BookingDetailDTO) -> some View {
        HStack(spacing: 0) {
            VStack(alignment: .leading, spacing: 4) {
                Text(LocalizedStringResource.BookingDetail.checkIn)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundStyle(.accent)

                Text(formattedDate(booking.fechaEntrada))
                    .font(.headline)
                    .fontWeight(.bold)

                if let checkIn = booking.hotel.checkIn {
                    Text(
                        String(
                            localized: .BookingDetail.fromTime(
                                formattedTime(checkIn)
                            )
                        )
                    )
                    .font(.caption)
                    .foregroundStyle(.secondary)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)

            Divider()
                .frame(height: 60)

            VStack(alignment: .leading, spacing: 4) {
                Text(LocalizedStringResource.BookingDetail.checkOut)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundStyle(.accent)

                Text(formattedDate(booking.fechaSalida))
                    .font(.headline)
                    .fontWeight(.bold)

                if let checkOut = booking.hotel.checkOut {
                    Text(
                        String(
                            localized: .BookingDetail.beforeTime(
                                formattedTime(checkOut)
                            )
                        )
                    )
                    .font(.caption)
                    .foregroundStyle(.secondary)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(.leading, 16)
        }
        .padding(16)
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .shadow(color: .black.opacity(0.07), radius: 8, y: 2)
    }

    // MARK: - Room Card

    private func roomCard(_ booking: BookingDetailDTO) -> some View {
        HStack(spacing: 12) {
            Image(systemName: "bed.double.fill")
                .foregroundStyle(.accent)
                .font(.title3)

            VStack(alignment: .leading, spacing: 4) {
                Text(booking.habitacion.nombre)
                    .font(.subheadline)
                    .fontWeight(.semibold)

                let details = roomDetailsText(booking)
                if !details.isEmpty {
                    Text(details)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }

            Spacer()
        }
        .padding(16)
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .shadow(color: .black.opacity(0.07), radius: 8, y: 2)
    }

    // MARK: - QR Code Card

    private var qrCodeCard: some View {
        VStack(spacing: 12) {
            Text(LocalizedStringResource.BookingDetail.qrTitle)
                .font(.subheadline)
                .fontWeight(.semibold)

            // QR placeholder
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.gray.opacity(0.1))
                .frame(width: 140, height: 140)
                .overlay {
                    Image(systemName: "qrcode")
                        .resizable()
                        .scaledToFit()
                        .padding(20)
                        .foregroundStyle(.gray.opacity(0.5))
                }

            Text(LocalizedStringResource.BookingDetail.qrDescription)
                .font(.caption)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 24)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 20)
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .shadow(color: .black.opacity(0.07), radius: 8, y: 2)
    }

    // MARK: - Contact Card

    private func contactCard(_ booking: BookingDetailDTO) -> some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(LocalizedStringResource.BookingDetail.hotelContact)
                .font(.headline)
                .fontWeight(.bold)

            if let phone = booking.hotel.contactoCelular, !phone.isEmpty {
                Button {
                    if let url = URL(string: "tel:\(phone.filter { $0.isNumber || $0 == "+" })") {
                        UIApplication.shared.open(url)
                    }
                } label: {
                    HStack(spacing: 12) {
                        Image(systemName: "phone.fill")
                            .foregroundStyle(.accent)
                            .frame(width: 32, height: 32)
                            .background(Color.accentColor.opacity(0.1))
                            .clipShape(Circle())

                        VStack(alignment: .leading, spacing: 2) {
                            Text(phone)
                                .font(.subheadline)
                                .fontWeight(.medium)
                                .foregroundStyle(.primary)
                            Text(LocalizedStringResource.BookingDetail.directFrontDesk)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }

                        Spacer()
                    }
                }
            }

            if let email = booking.hotel.contactoEmail, !email.isEmpty {
                Button {
                    if let url = URL(string: "mailto:\(email)") {
                        UIApplication.shared.open(url)
                    }
                } label: {
                    HStack(spacing: 12) {
                        Image(systemName: "envelope.fill")
                            .foregroundStyle(.accent)
                            .frame(width: 32, height: 32)
                            .background(Color.accentColor.opacity(0.1))
                            .clipShape(Circle())

                        VStack(alignment: .leading, spacing: 2) {
                            Text(email)
                                .font(.subheadline)
                                .fontWeight(.medium)
                                .foregroundStyle(.primary)
                            Text(LocalizedStringResource.BookingDetail.conciergeServices)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }

                        Spacer()
                    }
                }
            }
        }
        .padding(16)
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .shadow(color: .black.opacity(0.07), radius: 8, y: 2)
    }

    // MARK: - Footer Buttons

    private var footerButtons: some View {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withFullDate]
        formatter.timeZone = .current

        return HStack(spacing: 16) {
                NavigationLink {
                    if let hotel = self.viewModel.hotel,
                       let booking = self.viewModel.booking {
                        CreateBookingView(
                            hotel: hotel,
                            booking: ModifyBooking(
                                id: booking.id,
                                habitacionID: booking.habitacion.id,
                                fechaEntrada: formatter.date(from: booking.fechaEntrada) ?? .init(),
                                fechaSalida: formatter.date(from: booking.fechaSalida) ?? .init(),
                                numHuespedes: booking.numHuespedes
                            )
                        )
                    }
                } label: {
                    Text(LocalizedStringResource.BookingDetail.modify)
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundStyle(.accent)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                        .background(
                            Capsule()
                                .stroke(Color.accentColor, lineWidth: 2)
                        )
                }
                .disabled(viewModel.isCancelling || self.viewModel.booking == nil || self.viewModel.hotel == nil)

            Button(role: .destructive) {
                showCancelConfirmation = true
            } label: {
                Group {
                    if viewModel.isCancelling {
                        ProgressView()
                            .tint(.white)
                    } else {
                        Text(LocalizedStringResource.BookingDetail.cancel)
                    }
                }
                .font(.subheadline)
                .fontWeight(.semibold)
                .foregroundStyle(.white)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 14)
                .background(viewModel.isCancelling ? Color.red.opacity(0.5) : Color.red)
                .clipShape(Capsule())
            }
            .disabled(viewModel.isCancelling)
            .confirmationDialog(
                String(localized: .BookingDetail.cancelConfirmTitle),
                isPresented: $showCancelConfirmation,
                titleVisibility: .visible
            ) {
                Button(
                    String(localized: .BookingDetail.cancelConfirmAction),
                    role: .destructive
                ) {
                    Task {
                        await viewModel.cancelBooking(bookingId: bookingId)
                    }
                }
            } message: {
                Text(LocalizedStringResource.BookingDetail.cancelConfirmMessage)
            }
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 12)
        .background(Color(.systemBackground))
        .shadow(color: .black.opacity(0.05), radius: 8, y: -2)
    }

    // MARK: - Error View

    private var errorView: some View {
        VStack(spacing: 16) {
            Spacer()
            Image(systemName: "exclamationmark.triangle")
                .resizable()
                .scaledToFit()
                .frame(width: 56, height: 56)
                .foregroundStyle(.orange)

            Text(viewModel.errorMessage ?? String(localized: .BookingDetail.errorGeneric))
                .font(.body)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)

            Button {
                Task {
                    await viewModel.fetchDetail(bookingId: bookingId)
                }
            } label: {
                Text(LocalizedStringResource.BookingDetail.retry)
                    .fontWeight(.semibold)
                    .foregroundStyle(.white)
                    .padding(.horizontal, 32)
                    .padding(.vertical, 12)
                    .background(Color.blue)
                    .clipShape(Capsule())
            }
            Spacer()
        }
    }

    // MARK: - Helpers

    private static let inputDateFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        return f
    }()

    private static let displayDateFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateStyle = .medium
        return f
    }()

    private func formattedDate(_ dateString: String) -> String {
        guard let date = Self.inputDateFormatter.date(from: dateString) else {
            return dateString
        }
        return Self.displayDateFormatter.string(from: date)
    }

    private func formattedTime(_ timeString: String) -> String {
        // Input: "HH:mm:ss" or "HH:mm" → Output: "h:mm a"
        let parts = timeString.split(separator: ":")
        guard parts.count >= 2,
              let hour = Int(parts[0]),
              let minute = Int(parts[1]) else {
            return timeString
        }

        var components = DateComponents()
        components.hour = hour
        components.minute = minute

        guard let date = Calendar.current.date(from: components) else {
            return timeString
        }

        let formatter = DateFormatter()
        formatter.dateFormat = "h:mm a"
        return formatter.string(from: date)
    }

    private func hotelLocationText(_ hotel: BookingHotelDTO, address: String) -> String {
        var parts = [address]
        if let city = hotel.ciudad { parts.append(city) }
        if let country = hotel.pais { parts.append(country) }
        return parts.joined(separator: ", ")
    }

    private func roomDetailsText(_ booking: BookingDetailDTO) -> String {
        var parts: [String] = []
        parts.append(
            String(localized: .BookingDetail.guests(booking.numHuespedes))
        )

        let amenities = booking.amenidadesHotel.compactMap { raw in
            HotelAmenity(rawValue: raw)
        }
        let featured = amenities.filter(\.isFeatured).prefix(3)
        for amenity in featured {
            parts.append(String(localized: amenity.localizedName))
        }

        return parts.joined(separator: " · ")
    }
}

// MARK: - EstadoReserva Detail Helpers

extension EstadoReserva {
    var detailIcon: String {
        switch self {
        case .confirmada: return "checkmark.circle.fill"
        case .pendiente: return "clock.fill"
        case .cancelada: return "xmark.circle.fill"
        case .completada: return "checkmark.seal.fill"
        }
    }
}

#Preview {
    NavigationStack {
        BookingDetailView(bookingId: UUID())
    }
}
