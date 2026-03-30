//
//  Toast.swift
//  TravelHub
//
//  Created by Andres Donoso on 29/03/26.
//

import SwiftUI

enum ToastStyle {
    case success, error, warning, info
    
    var icon: String {
        switch self {
            case .success: return "checkmark.circle.fill"
            case .error: return "xmark.circle.fill"
            case .warning: return "exclamationmark.triangle.fill"
            case .info: return "info.circle.fill"
        }
    }
    
    var color: Color {
        switch self {
            case .success: return .successDark
            case .error: return .dangerDark
            case .warning: return .warningDark
            case .info: return .accentDark
        }
    }
    
    var background: Color {
        switch self {
            case .success: return .successLight
            case .error: return .dangerLight
            case .warning: return .warningLight
            case .info: return .accentLight
        }
    }
}

struct Toast: Equatable {
    let message: String
    let title: String?
    let style: ToastStyle
    var duration: Double
    
    init(message: String, title: String? = nil, style: ToastStyle, duration: Double = 3.0) {
        self.message = message
        self.style = style
        self.duration = duration
        self.title = title
    }
}
