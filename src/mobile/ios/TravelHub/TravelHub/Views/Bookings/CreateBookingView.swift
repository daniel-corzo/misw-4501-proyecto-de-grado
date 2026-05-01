//
//  CreateBookingView.swift
//  TravelHub
//
//  Created by Andres Donoso on 17/04/26.
//

import SwiftUI

struct CreateBookingView: View {
    let hotel: Hotel
    let booking: ModifyBooking?

    @Environment(\.bookingService) private var bookingService
    @Environment(\.toastManager) private var toastManager
    @Environment(\.dismiss) private var dismiss
    @Environment(Router.self) private var router

    @State private var viewModel = ViewModel()
    @State private var dateRange = DateRange(
        start: Calendar.current.date(byAdding: .day, value: 1, to: .now)!,
        end: Calendar.current.date(byAdding: .day, value: 2, to: .now)!
    )
    @State private var guests: Int = 1
    @State private var selectedHabitacion: Habitacion

    private var isButtonDisabled: Bool {
        print("Date Range: \(self.dateRange.start == self.dateRange.end)")
        print("Booking: \(self.booking != nil) | Was Modified: \(self.wasModified)")
        print("Is Loading: \(self.viewModel.isLoading)")

        if self.dateRange.start == self.dateRange.end {
            return true
        }

        if self.booking != nil && !self.wasModified {
            return true
        }

        if self.viewModel.isLoading {
            return true
        }

        return false
    }

    private var wasModified: Bool {
        if let booking = self.booking {
            return booking.habitacionID != self.selectedHabitacion.id
                || booking.fechaEntrada != self.dateRange.start
                || booking.fechaSalida != self.dateRange.end
                || booking.numHuespedes != self.guests
        }

        return false
    }

    private func getModificationValue() -> Double {
        guard let booking = self.booking else {
            return 0
        }

        let modificationBaseValue = self.hotel.valorMinimoModificacion
        let currentRoomValue =
            self.hotel.habitaciones.first(where: {
                $0.id == booking.habitacionID
            })?.monto ?? 0
        let newRoomValue = self.selectedHabitacion.monto

        return modificationBaseValue + max(newRoomValue - currentRoomValue, 0)
    }

    init(hotel: Hotel, booking: ModifyBooking? = nil) {
        self.hotel = hotel
        self.booking = booking
        self._selectedHabitacion = .init(
            initialValue: hotel.habitaciones.first!
        )
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 48) {

                HotelHeaderCardView(hotel: hotel)

                DateRangePickerView(dateRange: $dateRange)

                GuestsCounterView(
                    guests: $guests,
                    minimum: 1,
                    maximum: self.selectedHabitacion.capacidad
                )

                RoomSelectorView(
                    habitaciones: hotel.habitaciones,
                    selectedHabitacion: $selectedHabitacion
                )

                if booking == nil {
                    PriceBreakdownView(
                        habitacion: self.selectedHabitacion,
                        dateRange: dateRange
                    )
                } else {
                    VStack(spacing: 12) {
                        HStack {
                            Text(
                                LocalizedStringResource.CreateBooking
                                    .totalForModify
                            )
                            .font(.headline)
                            .fontWeight(.bold)

                            Spacer()

                            Text(
                                "$\(self.getModificationValue().formatted(.number))"
                            )
                            .font(.title3)
                            .fontWeight(.bold)
                            .contentTransition(.numericText(countsDown: false))
                            .foregroundStyle(.accent)
                        }  //: HStack
                    }  //: VStack
                    .padding()
                    .background(Color.formBackground)
                    .clipShape(RoundedRectangle(cornerRadius: 20))
                }

                Spacer(minLength: 80)
            }
            .padding(.horizontal, 20)
            .padding(.top, 16)
        }
        .navigationTitle(
            LocalizedStringResource.CreateBooking.navigationTitle
        )
        .navigationBarTitleDisplayMode(.inline)
        .safeAreaInset(edge: .bottom) {
            Button {
                // TODO: Navigate to payment
                Task {
                    if let booking = self.booking {
                        let didSave = await self.viewModel.modify(
                            id: booking.id,
                            habitacionId: self.selectedHabitacion.id,
                            fechaEntrada: self.dateRange.start,
                            fechaSalida: self.dateRange.end,
                            numHuespedes: self.guests
                        )

                        if didSave {
                            dismiss()
                        }
                    } else {
                        let didSave = await self.viewModel.create(
                            habitacionId: selectedHabitacion.id,
                            fechaEntrada: self.dateRange.start,
                            fechaSalida: self.dateRange.end,
                            numHuespedes: self.guests
                        )

                        if didSave {
                            router.switchTab(to: .bookings)
                        }
                    }
                }
            } label: {
                HStack {
                    Text(
                        booking == nil
                            ? LocalizedStringResource.CreateBooking.createBooking
                            : LocalizedStringResource.CreateBooking.modifyBooking
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
            .background(.ultraThinMaterial)
        }
        .task {
            self.viewModel.bookingService = self.bookingService
            self.viewModel.toastManager = self.toastManager
        }
        .onAppear {
            if let booking = self.booking {
                self.dateRange = .init(
                    start: booking.fechaEntrada,
                    end: booking.fechaSalida
                )
                self.guests = booking.numHuespedes
                self.selectedHabitacion = self.hotel.habitaciones.first(where: {
                    $0.id == booking.habitacionID
                }) ?? self.hotel.habitaciones.first!
            } else {
                self.selectedHabitacion = self.hotel.habitaciones.first!
            }
        }
        .onChange(of: self.selectedHabitacion) { _, newValue in
            self.guests = min(newValue.capacidad, self.guests)
        }
    }
}

#Preview {
    let habitaciones = [
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
    ]

    NavigationStack {
        CreateBookingView(
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
                valorMinimoModificacion: 100000,
                politicas: [],
                habitaciones: habitaciones,
                precioMinimo: 420000
            ),
            booking: ModifyBooking(
                id: UUID(),
                habitacionID: habitaciones.first!.id,
                fechaEntrada: Calendar.current.date(
                    byAdding: .day,
                    value: 10,
                    to: .now
                )!,
                fechaSalida: Calendar.current.date(
                    byAdding: .day,
                    value: 20,
                    to: .now
                )!,
                numHuespedes: 2
            )
        )
    }
}
