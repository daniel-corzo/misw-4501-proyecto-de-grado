//
//  GuestsCounterView.swift
//  TravelHub
//
//  Created by Andres Donoso on 17/04/26.
//

import SwiftUI

struct GuestsCounterView: View {

    @Binding var guests: Int

    let minimum: Int
    let maximum: Int

    var body: some View {
        HStack {
            Text(LocalizedStringResource.CreateBooking.guests)
                .font(.headline)

            Spacer()

            HStack(spacing: 16) {
                Button {
                    withAnimation(.spring(response: 0.3, dampingFraction: 0.7))
                    {
                        if guests > minimum { guests -= 1 }
                    }
                } label: {
                    Image(systemName: "minus")
                        .fontWeight(.medium)
                        .frame(width: 36, height: 36)
                        .background(Color(.systemBackground))
                        .clipShape(Circle())
                        .overlay(
                            Circle().stroke(Color(.systemGray5), lineWidth: 1)
                        )
                }
                .disabled(guests <= minimum)

                Text("\(guests)")
                    .font(.headline)
                    .monospacedDigit()
                    .contentTransition(.numericText())
                    .animation(
                        .spring(response: 0.3, dampingFraction: 0.7),
                        value: guests
                    )
                    .frame(minWidth: 20)

                Button {
                    withAnimation(.spring(response: 0.3, dampingFraction: 0.7))
                    {
                        if guests < maximum { guests += 1 }
                    }
                } label: {
                    Image(systemName: "plus")
                        .fontWeight(.medium)
                        .foregroundStyle(.white)
                        .frame(width: 36, height: 36)
                        .background(
                            guests < maximum
                                ? Color.accentColor : Color(.systemGray4)
                        )
                        .clipShape(Circle())
                }
                .disabled(guests >= maximum)

            }  //: HStack Controls
        }  //: HStack
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 50))
        .shadow(color: .black.opacity(0.07), radius: 8, x: 0, y: 2)
    }
}

#Preview {
    @Previewable @State var guests = 2

    GuestsCounterView(guests: $guests, minimum: 1, maximum: 10)
        .padding()
        .background(Color(red: 0.965, green: 0.969, blue: 0.973))
}
