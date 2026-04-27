//
//  ReservationDetailView.swift
//  TravelHub
//

import SwiftUI

struct ReservationDetailView: View {
    let reservationId: UUID

    @Environment(\.reservationService) private var reservationService
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
            } else if let reservation = viewModel.reservation {
                successView(reservation)
            }
        }
        .navigationTitle(LocalizedStringResource.ReservationDetail.navigationTitle)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar(.hidden, for: .tabBar)
        .task {
            viewModel.reservationService = reservationService
            viewModel.toastManager = toastManager
            viewModel.hotelService = hotelService
            await viewModel.fetchDetail(reservationId: reservationId)
            
            if let reservation = self.viewModel.reservation, let hotelId = reservation.hotel.id {
                await viewModel.fetchHotelDetail(id: hotelId)
            }
        }
        .refreshable {
            await viewModel.fetchDetail(reservationId: reservationId)
        }
        .onChange(of: viewModel.didCancel) { _, didCancel in
            if didCancel {
                dismiss()
            }
        }
    }

    // MARK: - Success Content

    private func successView(_ reservation: ReservationDetailDTO) -> some View {
        VStack(spacing: 0) {
            ScrollView {
                VStack(spacing: 20) {
                    statusCard(reservation)
                    hotelCard(reservation)
                    datesCard(reservation)
                    roomCard(reservation)
                    qrCodeCard
                    contactCard(reservation)
                }
                .padding(.horizontal, 20)
                .padding(.top, 16)
                .padding(.bottom, 24)
            }

            if reservation.estado == .confirmada || reservation.estado == .pendiente {
                footerButtons
            }
        }
    }

    // MARK: - Status Card

    private func statusCard(_ reservation: ReservationDetailDTO) -> some View {
        VStack(spacing: 12) {
            Image(systemName: reservation.estado.detailIcon)
                .resizable()
                .scaledToFit()
                .frame(width: 48, height: 48)
                .foregroundStyle(reservation.estado.badgeColor)

            Text(reservation.estado.badgeLabel)
                .font(.headline)
                .fontWeight(.bold)
                .foregroundStyle(reservation.estado.badgeColor)

            Text(
                String(
                    localized: .ReservationDetail.bookingId(
                        reservation.codigoReserva
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

    private func hotelCard(_ reservation: ReservationDetailDTO) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            // Hotel image
            AsyncImage(url: reservation.hotel.imagenes.first.flatMap { URL(string: $0) }) { phase in
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
                    Text(reservation.hotel.nombre)
                        .font(.title3)
                        .fontWeight(.bold)

                    Spacer()

                    if let stars = reservation.hotel.estrellas {
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

                if let address = reservation.hotel.direccion {
                    HStack(spacing: 4) {
                        Image(systemName: "mappin.and.ellipse")
                            .font(.caption)
                        Text(hotelLocationText(reservation.hotel, address: address))
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

    private func datesCard(_ reservation: ReservationDetailDTO) -> some View {
        HStack(spacing: 0) {
            VStack(alignment: .leading, spacing: 4) {
                Text(LocalizedStringResource.ReservationDetail.checkIn)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundStyle(.accent)

                Text(formattedDate(reservation.fechaEntrada))
                    .font(.headline)
                    .fontWeight(.bold)

                if let checkIn = reservation.hotel.checkIn {
                    Text(
                        String(
                            localized: .ReservationDetail.fromTime(
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
                Text(LocalizedStringResource.ReservationDetail.checkOut)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundStyle(.accent)

                Text(formattedDate(reservation.fechaSalida))
                    .font(.headline)
                    .fontWeight(.bold)

                if let checkOut = reservation.hotel.checkOut {
                    Text(
                        String(
                            localized: .ReservationDetail.beforeTime(
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

    private func roomCard(_ reservation: ReservationDetailDTO) -> some View {
        HStack(spacing: 12) {
            Image(systemName: "bed.double.fill")
                .foregroundStyle(.accent)
                .font(.title3)

            VStack(alignment: .leading, spacing: 4) {
                Text(reservation.habitacion.nombre)
                    .font(.subheadline)
                    .fontWeight(.semibold)

                let details = roomDetailsText(reservation)
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
            Text(LocalizedStringResource.ReservationDetail.qrTitle)
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

            Text(LocalizedStringResource.ReservationDetail.qrDescription)
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

    private func contactCard(_ reservation: ReservationDetailDTO) -> some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(LocalizedStringResource.ReservationDetail.hotelContact)
                .font(.headline)
                .fontWeight(.bold)

            if let phone = reservation.hotel.contactoCelular, !phone.isEmpty {
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
                            Text(LocalizedStringResource.ReservationDetail.directFrontDesk)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }

                        Spacer()
                    }
                }
            }

            if let email = reservation.hotel.contactoEmail, !email.isEmpty {
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
                            Text(LocalizedStringResource.ReservationDetail.conciergeServices)
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
                       let reservation = self.viewModel.reservation {
                        CreateReservationView(
                            hotel: hotel,
                            reservation: ModifyReservation(
                                id: reservation.id,
                                habitacionID: reservation.habitacion.id,
                                fechaEntrada: formatter.date(from: reservation.fechaEntrada) ?? .init(),
                                fechaSalida: formatter.date(from: reservation.fechaSalida) ?? .init(),
                                numHuespedes: reservation.numHuespedes
                            )
                        )
                    }
                } label: {
                    Text(LocalizedStringResource.ReservationDetail.modify)
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
                .disabled(viewModel.isCancelling || self.viewModel.reservation == nil || self.viewModel.hotel == nil)

            Button(role: .destructive) {
                showCancelConfirmation = true
            } label: {
                Group {
                    if viewModel.isCancelling {
                        ProgressView()
                            .tint(.white)
                    } else {
                        Text(LocalizedStringResource.ReservationDetail.cancel)
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
                String(localized: .ReservationDetail.cancelConfirmTitle),
                isPresented: $showCancelConfirmation,
                titleVisibility: .visible
            ) {
                Button(
                    String(localized: .ReservationDetail.cancelConfirmAction),
                    role: .destructive
                ) {
                    Task {
                        await viewModel.cancelReservation(reservationId: reservationId)
                    }
                }
            } message: {
                Text(LocalizedStringResource.ReservationDetail.cancelConfirmMessage)
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

            Text(viewModel.errorMessage ?? String(localized: .ReservationDetail.errorGeneric))
                .font(.body)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)

            Button {
                Task {
                    await viewModel.fetchDetail(reservationId: reservationId)
                }
            } label: {
                Text(LocalizedStringResource.ReservationDetail.retry)
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

    private func hotelLocationText(_ hotel: ReservationHotelDTO, address: String) -> String {
        var parts = [address]
        if let city = hotel.ciudad { parts.append(city) }
        if let country = hotel.pais { parts.append(country) }
        return parts.joined(separator: ", ")
    }

    private func roomDetailsText(_ reservation: ReservationDetailDTO) -> String {
        var parts: [String] = []
        parts.append(
            String(localized: .ReservationDetail.guests(reservation.numHuespedes))
        )

        let amenities = reservation.amenidadesHotel.compactMap { raw in
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
        ReservationDetailView(reservationId: UUID())
    }
}
