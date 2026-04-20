//
//  CreateReservationView.swift
//  TravelHub
//
//  Created by Andres Donoso on 17/04/26.
//

import SwiftUI

struct CreateReservationView: View {
    let hotel: Hotel

    @Environment(\.reservationService) private var reservationService
    @Environment(\.toastManager) private var toastManager

    @State private var viewModel = ViewModel()
    @State private var dateRange = DateRange(
        start: Calendar.current.date(byAdding: .day, value: 1, to: .now)!,
        end: Calendar.current.date(byAdding: .day, value: 2, to: .now)!
    )
    @State private var guests: Int = 1
    @State private var selectedHabitacion: Habitacion?

    private var selectedOrFirst: Habitacion? {
        selectedHabitacion ?? hotel.habitaciones.first
    }
    
    private var isButtonDisabled: Bool {
        if self.dateRange.start == self.dateRange.end {
            return true
        }
        
        if self.selectedHabitacion == nil {
            return true
        }
        
        return false
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 48) {

                HotelHeaderCardView(hotel: hotel)

                DateRangePickerView(dateRange: $dateRange)

                GuestsCounterView(guests: $guests, minimum: 1, maximum: 10)

                RoomSelectorView(
                    habitaciones: hotel.habitaciones,
                    selectedHabitacion: $selectedHabitacion
                )

                if let habitacion = selectedOrFirst {
                    PriceBreakdownView(
                        habitacion: habitacion,
                        dateRange: dateRange
                    )
                }

                Spacer(minLength: 80)
            }
            .padding(.horizontal, 20)
            .padding(.top, 16)
        }
        .navigationTitle(
            LocalizedStringResource.CreateReservation.navigationTitle
        )
        .navigationBarTitleDisplayMode(.inline)
        .safeAreaInset(edge: .bottom) {
            Button {
                // TODO: Navigate to payment
                if let selectedHabitacion = self.selectedHabitacion {
                    Task {
                        await self.viewModel.create(
                            habitacionId: selectedHabitacion.id,
                            fechaEntrada: self.dateRange.start,
                            fechaSalida: self.dateRange.end,
                            numHuespedes: self.guests
                        )
                    }
                }
            } label: {
                HStack {
                    Text(
                        LocalizedStringResource.CreateReservation
                            .proceedToPayment
                    )
                    .font(.headline)
                    .fontWeight(.semibold)

                    Image(systemName: "arrow.right")
                        .fontWeight(.semibold)
                }
                .foregroundStyle(.white)
                .frame(maxWidth: .infinity)
                .capsuleButton(disabled: self.isButtonDisabled)
                .padding(.horizontal, 20)
                .padding(.bottom, 8)
                .disabled(self.isButtonDisabled)
            }
            .disabled(selectedOrFirst == nil)
            .background(.ultraThinMaterial)
        }
        .task {
            self.viewModel.reservationService = self.reservationService
            self.viewModel.toastManager = self.toastManager
        }
    }
}

#Preview {
    NavigationStack {
        CreateReservationView(
            hotel: Hotel(
                id: UUID(),
                nombre: "Grand Plaza Hotel",
                direccion: "Calle 123 # 45-67",
                pais: "Colombia",
                estado: "Cundinamarca",
                departamento: "Cundinamarca",
                ciudad: "Bogotá",
                descripcion:
                    "A luxury hotel in the heart of Bogotá with world-class amenities.",
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
                habitaciones: [
                    Habitacion(
                        id: UUID(),
                        capacidad: 2,
                        numero: "101",
                        descripcion:
                            "Comfortable room with a stunning city view and king-size bed.",
                        imagenes: [
                            "https://cf.bstatic.com/xdata/images/hotel/max1024x768/837215020.jpg"
                        ],
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
                        imagenes: [
                            "https://www.maritim.com/fileadmin/_processed_/0/1/csm_Bpa_363_Superior_500a005b62.jpg"
                        ],
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
                        imagenes: [
                            "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/2c/29/84/e3/486104-guest-room.jpg"
                        ],
                        monto: 820000,
                        impuestos: 120000,
                        disponible: false
                    ),
                ],
                precioMinimo: 420000
            )
        )
    }
}
