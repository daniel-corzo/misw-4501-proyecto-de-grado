//
//  EnvironmentKeys.swift
//  TravelHub
//
//  Created by Andres Donoso on 29/03/26.
//

import SwiftUI

extension EnvironmentValues {
    var toastManager: ToastManager {
        get { self[ToastManagerKey.self] }
        set { self[ToastManagerKey.self] = newValue }
    }
}

struct ToastManagerKey: EnvironmentKey {
    static let defaultValue = ToastManager()
}
