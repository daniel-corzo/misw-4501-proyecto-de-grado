//
//  RoomSelectorView.swift
//  TravelHub
//
//  Created by Andres Donoso on 17/04/26.
//

import SwiftUI

struct RoomSelectorView: View {

    let habitaciones: [Habitacion]
    @Binding var selectedHabitacion: Habitacion

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {

            Text(LocalizedStringResource.CreateReservation.selectRoom)
                .font(.title3)
                .fontWeight(.bold)

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    ForEach(habitaciones) { habitacion in
                        RoomCard(
                            habitacion: habitacion,
                            isSelected: selectedHabitacion.id == habitacion.id,
                            onTap: {
                                withAnimation(
                                    .spring(
                                        response: 0.35,
                                        dampingFraction: 0.7
                                    )
                                ) {
                                    selectedHabitacion = habitacion
                                }
                            }
                        )
                    }
                }
                .padding(.horizontal, 2)
                .padding(.vertical, 4)
            }
        }
    }
}

private struct RoomCard: View {

    let habitacion: Habitacion
    let isSelected: Bool
    let onTap: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {

            ZStack(alignment: .topTrailing) {
                AsyncImage(url: URL(string: habitacion.imagenes.first ?? "")) {
                    phase in
                    switch phase {
                    case .success(let image):
                        image
                            .resizable()
                            .scaledToFill()
                    case .failure, .empty:
                        Image(systemName: "bed.double.fill")
                            .resizable()
                            .scaledToFit()
                            .padding(30)
                            .foregroundStyle(.secondary)
                    @unknown default:
                        ProgressView()
                    }
                }
                .frame(width: 140, height: 140)
                .clipShape(RoundedRectangle(cornerRadius: 70))

                if isSelected {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.title2)
                        .foregroundStyle(.accent)
                        .background(
                            Color(.systemBackground).clipShape(Circle())
                        )
                        .transition(.scale.combined(with: .opacity))
                }
            }

            VStack(alignment: .leading, spacing: 2) {
                Text(habitacion.descripcion ?? String(localized: LocalizedStringResource.CreateReservation.roomNumber(roomNumber: habitacion.numero)))
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .foregroundStyle(.primary)
                    .lineLimit(1)

                HStack(alignment: .firstTextBaseline, spacing: 2) {
                    Text("$\(habitacion.monto.formatted(.number))")
                        .font(.subheadline)
                        .fontWeight(.bold)
                        .foregroundStyle(isSelected ? .accent : .primary)

                    Text(LocalizedStringResource.CreateReservation.perNight)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
        }
        .padding(12)
        .frame(width: 164)
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 20))
        .overlay(
            RoundedRectangle(cornerRadius: 20)
                .stroke(
                    isSelected ? Color.accentColor : Color.clear,
                    lineWidth: 2
                )
        )
        .shadow(color: .black.opacity(0.07), radius: 8, x: 0, y: 2)
        .onTapGesture { onTap() }
    }
}

#Preview {
    @Previewable @State var selected: Habitacion = Habitacion(
        id: UUID(),
        capacidad: 2,
        numero: "101",
        descripcion:
            "Comfortable room with a stunning city view and king-size bed.",
        imagenes: ["https://dynamic-media-cdn.tripadvisor.com/media/photo-o/1b/48/52/32/ek-hotel.jpg"],
        monto: 420000,
        impuestos: 80000,
        disponible: true
    )

    let habitaciones = [
        Habitacion(
            id: UUID(),
            capacidad: 2,
            numero: "101",
            descripcion:
                "Comfortable room with a stunning city view and king-size bed.",
            imagenes: ["https://cf.bstatic.com/xdata/images/hotel/max1024x768/837215020.jpg"],
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
            imagenes: ["https://www.maritim.com/fileadmin/_processed_/0/1/csm_Bpa_363_Superior_500a005b62.jpg"],
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
            imagenes: ["https://dynamic-media-cdn.tripadvisor.com/media/photo-o/2c/29/84/e3/486104-guest-room.jpg"],
            monto: 820000,
            impuestos: 120000,
            disponible: false
        ),
    ]

    RoomSelectorView(
        habitaciones: habitaciones,
        selectedHabitacion: $selected
    )
    .padding()
    .background(Color(red: 0.965, green: 0.969, blue: 0.973))
}
