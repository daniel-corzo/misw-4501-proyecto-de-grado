//
//  CapsuleButton.swift
//  TravelHub
//
//  Created by Andres Donoso on 24/03/26.
//

import SwiftUI

struct CapsuleButtonModifier: ViewModifier {
    var disabled: Bool = false

    func body(content: Content) -> some View {
        content
            .padding(.vertical, 24)
            .glassEffect(
                disabled
                    ? .regular.tint(.neutralLight)
                    : .regular.tint(.accent).interactive()
            )
            .clipShape(.capsule)
            .shadow(
                color: disabled ? .clear : .accent.opacity(0.2),
                radius: 15,
                y: 10
            )
    }
}

extension View {
    func capsuleButton(disabled: Bool = false) -> some View {
        modifier(CapsuleButtonModifier(disabled: disabled))
    }
}

#Preview(traits: .sizeThatFitsLayout) {
    Button {
    } label: {
        Spacer()

        Text("Some Button")
            .foregroundStyle(.white)

        Spacer()
    }
    .capsuleButton(disabled: false)
    .padding()

    Button {
    } label: {
        Spacer()

        Text("Some Button")
            .foregroundStyle(.white)

        Spacer()
    }
    .capsuleButton(disabled: true)
    .padding()
}
