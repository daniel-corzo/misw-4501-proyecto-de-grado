//
//  ToastModifier.swift
//  TravelHub
//
//  Created by Andres Donoso on 29/03/26.
//

import SwiftUI

struct ToastModifier: ViewModifier {
    let toastManager: ToastManager
    
    func body(content: Content) -> some View {
        ZStack(alignment: .top) {
            content
            
            if let toast = toastManager.toast {
                ToastView(toast: toast)
                    .transition(.move(edge: .top).combined(with: .opacity))
                    .zIndex(999)
            }
        }
        .animation(.spring(), value: toastManager.toast)
    }
}

extension View {
    func toastOverlay(toastManager: ToastManager) -> some View {
        modifier(ToastModifier(toastManager: toastManager))
    }
}
