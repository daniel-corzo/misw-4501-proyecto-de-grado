//
//  CapsuleButton.swift
//  TravelHub
//
//  Created by Andres Donoso on 24/03/26.
//

import SwiftUI

struct CapsuleButtonModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding(.vertical, 24)
            .glassEffect(.regular.tint(.accent).interactive())
            .clipShape(.capsule)
            .shadow(color: .accent.opacity(0.2), radius: 15, y: 10)
            .glassEffect()
    }
}

extension View {
    func capsuleButton() -> some View {
        modifier(CapsuleButtonModifier())
    }
}
