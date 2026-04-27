//
//  HotelHeaderCardView.swift
//  TravelHub
//
//  Created by Andres Donoso on 17/04/26.
//

import SwiftUI

struct HotelHeaderCardView: View {

    let hotel: Hotel

    var body: some View {
        HStack(spacing: 16) {

            // MARK: Text content
            VStack(alignment: .leading, spacing: 6) {
                Text(
                    String(
                        localized: LocalizedStringResource.CreateReservation
                            .selectedHotel
                    ).uppercased()
                )
                .font(.caption2)
                .fontWeight(.semibold)
                .foregroundStyle(.secondary)
                .tracking(0.5)

                Text(hotel.nombre)
                    .font(.title3)
                    .fontWeight(.bold)
                    .foregroundStyle(.primary)

                // Star rating
                HStack(spacing: 4) {
                    Image(systemName: "star")
                    Text(
                        hotel.ranking.formatted(
                            .number.precision(.fractionLength(1))
                        )
                    )
                }
                .font(.subheadline)
                .foregroundStyle(.accent)
            }  //: VStack

            Spacer()

            // MARK: Hotel image
            AsyncImage(url: URL(string: hotel.images.first ?? "")) { phase in
                switch phase {
                case .success(let image):
                    image
                        .resizable()
                        .scaledToFill()
                case .failure, .empty:
                    Image(systemName: "building.2.fill")
                        .resizable()
                        .scaledToFit()
                        .padding(20)
                        .foregroundStyle(.secondary)
                @unknown default:
                    ProgressView()
                }
            }  //: AsyncImage
            .frame(width: 80, height: 80)
            .clipShape(Circle())

        }  //: HStack
        .padding(16)
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .shadow(color: .black.opacity(0.07), radius: 8, x: 0, y: 2)
    }
}

// MARK: - Preview

#Preview {
    let habitaciones = [
        Habitacion(
            id: UUID(),
            capacidad: 2,
            numero: "101",
            descripcion:
                "Comfortable room with a stunning city view and king-size bed.",
            imagenes: [],
            monto: 420000,
            impuestos: 80000,
            disponible: true
        ),
        Habitacion(
            id: UUID(),
            capacidad: 3,
            numero: "202",
            descripcion:
                "Spacious deluxe suite with separate living area and panoramic views.",
            imagenes: [],
            monto: 450000,
            impuestos: 90000,
            disponible: true
        ),
        Habitacion(
            id: UUID(),
            capacidad: 4,
            numero: "301",
            descripcion:
                "Premium suite with private terrace, jacuzzi and butler service.",
            imagenes: [],
            monto: 820000,
            impuestos: 120000,
            disponible: false
        ),
    ]

    HotelHeaderCardView(
        hotel: Hotel(
            id: UUID(),
            nombre: "Grand Plaza Hotel",
            direccion: "Calle 123 # 45-67",
            pais: "Colombia",
            estado: "Cundinamarca",
            departamento: "Cundinamarca",
            ciudad: "Bogotá",
            descripcion:
                "A luxury hotel in the heart of Bogotá with world-class amenities and breathtaking city views.",
            amenidades: [
                .pool, .wifi, .gym, .spa, .parking, .breakfastIncluded,
            ],
            estrellas: 4,
            ranking: 4.7,
            contactoCelular: "+57 300 000 0000",
            contactoEmail: "invalid-email.com",
            images: [],
            checkInHour: "14:00",
            checkOutHour: "12:00",
            valorMinimoModificacion: 24,
            politicas: [],
            habitaciones: habitaciones,
            precioMinimo: 420000
        )
    )
    .padding()
    .background(Color("#F6F7F8"))
}
