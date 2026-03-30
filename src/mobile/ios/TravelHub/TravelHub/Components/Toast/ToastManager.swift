//
//  ToastManager.swift
//  TravelHub
//
//  Created by Andres Donoso on 29/03/26.
//

import SwiftUI

@Observable
class ToastManager {
    var toast: Toast? = nil

    func show(_ message: String, title: String? = nil, style: ToastStyle) {
        withAnimation(.spring()) {
            toast = Toast(message: message, title: title, style: style)
        }

        DispatchQueue.main.asyncAfter(
            deadline: .now() + (toast?.duration ?? 3.0)
        ) {
            withAnimation(.spring()) {
                self.toast = nil
            }
        }
    }

    func success(_ message: String, title: String? = nil) {
        show(message, title: title, style: .success)
    }
    func error(_ message: String, title: String? = nil) {
        show(message, title: title, style: .error)
    }
    func warning(_ message: String, title: String? = nil) {
        show(message, title: title, style: .warning)
    }
    func info(_ message: String, title: String? = nil) {
        show(message, title: title, style: .info)
    }
}
