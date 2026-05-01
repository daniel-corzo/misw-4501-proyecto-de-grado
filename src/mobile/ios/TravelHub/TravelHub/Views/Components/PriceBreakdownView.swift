//
//  PriceBreakdownView.swift
//  TravelHub
//
//  Created by Andres Donoso on 17/04/26.
//
import SwiftUI

struct PriceBreakdownView: View {

    let habitacion: Habitacion
    let dateRange: DateRange

    private var nights: Int {
        Calendar.current.dateComponents(
            [.day],
            from: dateRange.start,
            to: dateRange.end
        ).day ?? 0
    }

    private var subtotal: Double { habitacion.monto * Double(nights) }
    private var serviceFee: Double { 0 }
    private var total: Double { subtotal + habitacion.impuestos + serviceFee }

    var body: some View {
        VStack(spacing: 12) {

            PriceRow(
                label:
                    String(localized: .CreateBooking.pricePerNight(pricePerNight: habitacion.monto.formatted(.number), nights: nights)),
                amount: subtotal
            )

            PriceRow(label: String(localized: .CreateBooking.serviceFee), amount: serviceFee)

            PriceRow(label: String(localized: .CreateBooking.occupancyTaxes), amount: habitacion.impuestos)

            Divider()

            HStack {
                Text(LocalizedStringResource.CreateBooking.total)
                    .font(.headline)
                    .fontWeight(.bold)

                Spacer()

                Text("$\(total.formatted(.number))")
                    .font(.title3)
                    .fontWeight(.bold)
                    .contentTransition(.numericText(countsDown: false))
                    .foregroundStyle(.accent)
            } //: HStack
        } //: VStack
        .padding()
        .background(Color.formBackground)
        .clipShape(RoundedRectangle(cornerRadius: 20))
    }
}

private struct PriceRow: View {

    let label: String
    let amount: Double

    var body: some View {
        HStack {
            Text(label)
                .font(.subheadline)
                .foregroundStyle(.secondary)

            Spacer()

            Text("$\(amount.formatted(.number))")
                .font(.subheadline)
                .foregroundStyle(.primary)
                .contentTransition(.numericText(countsDown: false))
        }
    }
}

#Preview {
    let habitacion = Habitacion(
        id: UUID(),
        capacidad: 2,
        numero: "101",
        descripcion:
            "Comfortable room with a stunning city view and king-size bed.",
        imagenes: [],
        monto: 420000,
        impuestos: 80000,
        disponible: true
    )

    let dateRange = DateRange(
        start: .now,
        end: Calendar.current.date(byAdding: .day, value: 5, to: .now)!
    )

    PriceBreakdownView(habitacion: habitacion, dateRange: dateRange)
        .padding()
}
