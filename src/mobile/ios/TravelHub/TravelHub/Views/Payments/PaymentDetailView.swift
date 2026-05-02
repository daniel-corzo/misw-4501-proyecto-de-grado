//
//  PaymentDetailView.swift
//  TravelHub
//
//  Created by Andres Donoso on 2/05/26.
//

import SwiftUI

struct PaymentDetailView: View {
    @Environment(\.paymentService) private var paymentService
    @Environment(\.toastManager) private var toastManager

    var subtotal: Double
    var taxesAndFees: Double
    var hotel: Hotel
    var nights: Int

    @State private var viewModel = ViewModel()
    @State private var cardholderName: String = ""
    @State private var cardNumber: String = ""
    @State private var expirationDate: String = ""
    @State private var cvc: String = ""

    private var total: Double {
        subtotal + taxesAndFees
    }

    var body: some View {
        VStack {
            // MARK: - Summary
            VStack(alignment: .leading, spacing: 16) {
                Text(LocalizedStringResource.Payment.summary)
                    .font(.title3)
                    .bold()

                HStack {
                    Text(
                        "\(hotel.nombre) (\(LocalizedStringResource.Payment.nights(numNights: nights)))"
                    )
                    .font(.system(size: 14))
                    .foregroundStyle(.neutralDark)

                    Spacer()

                    Text(subtotal.formatted(.currency(code: "COP")))
                }

                HStack {
                    Text(LocalizedStringResource.Payment.serviceFeesAndTaxes)
                        .font(.system(size: 14))
                        .foregroundStyle(.neutralDark)

                    Spacer()

                    Text(taxesAndFees.formatted(.currency(code: "COP")))
                }

                Divider()

                HStack {
                    Text(LocalizedStringResource.Payment.totalAmount)
                        .bold()

                    Spacer()

                    Text(total.formatted(.currency(code: "COP")))
                        .bold()
                        .foregroundStyle(.accent)
                }
            }  //: VStack Summary
            .padding()
            .background(Color.white)
            .clipShape(RoundedRectangle(cornerRadius: 20))
            .padding()

            HStack {
                Rectangle()
                    .frame(width: .infinity, height: 1)
                    .foregroundStyle(.neutralLight)

                Text(LocalizedStringResource.Payment.payWithCard)
                    .textCase(.uppercase)
                    .foregroundStyle(.neutralDark)
                    .font(.caption)
                    .bold()

                Rectangle()
                    .frame(width: .infinity, height: 1)
                    .foregroundStyle(.neutralLight)
            }
            .padding()

            // MARK: - Form
            VStack(spacing: 16) {
                FormTextFieldView(
                    fieldName: .Payment.cardholderName,
                    icon: "",
                    placeholder: "John Doe",
                    text: $cardholderName
                )

                FormTextFieldView(
                    fieldName: .Payment.cardNumber,
                    icon: "creditcard",
                    placeholder: "0000 0000 0000 0000",
                    text: $cardNumber
                )

                HStack {
                    FormTextFieldView(
                        fieldName: .Payment.expirationDate,
                        icon: "",
                        placeholder: .Payment.expirationDatePlaceholder,
                        text: $expirationDate
                    )

                    FormTextFieldView(
                        fieldName: .Payment.cvv,
                        icon: "",
                        placeholder: "•••",
                        isSecuredField: true,
                        text: $cvc
                    )
                }
            }  //: VStack Form
            .padding()

            Spacer()

            HStack {
                Image(systemName: "lock")

                Text(LocalizedStringResource.Payment.encryptionInfo)
            }
            .font(.caption)
            .foregroundStyle(.neutralDark)

            Button {
                Task {
                    await self.viewModel.pay(
                        monto: Int(self.total),
                        medioDePago: "credit_card",
                        creditCardNumber: self.cardNumber,
                        cardholderName: self.cardholderName,
                        cvv: self.cvc,
                        expirationDate: self.expirationDate
                    )
                }
            } label: {
                Spacer()

                Text(
                    LocalizedStringResource.Payment.confirmPayment(
                        totalAmount: self.total.formatted(
                            .currency(code: "COP")
                        )
                    )
                )

                Image(systemName: "chevron.forward")

                Spacer()
            }
            .bold()
            .foregroundStyle(.white)
            .capsuleButton()
            .padding(.horizontal)

        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
        .background(Color.formBackground)
        .navigationTitle(LocalizedStringResource.Payment.checkout)
        .navigationBarTitleDisplayMode(.inline)
        .task {
            self.viewModel.paymentService = self.paymentService
            self.viewModel.toastManager = self.toastManager
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
        PaymentDetailView(
            subtotal: 1_000_000,
            taxesAndFees: 100_000,
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
            nights: 5
        )
    }
}
