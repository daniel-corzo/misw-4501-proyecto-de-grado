//
//  Formatters.swift
//  TravelHub
//
//  Created by Andres Donoso on 17/03/26.
//

import Foundation

/// Formats a string of digits into a phone number format: `(XXX) XXX-XXXX`.
///
/// Non-numeric characters are stripped before formatting, and input is capped at 10 digits.
/// The format is applied progressively as the number of digits grows:
/// - 1–3 digits: `(XXX`
/// - 4–6 digits: `(XXX) XXX`
/// - 7–10 digits: `(XXX) XXX-XXXX`
///
/// - Parameter number: The raw input string, may contain non-numeric characters.
/// - Returns: A formatted phone number string.
///
/// - Example:
/// ```swift
/// formatPhone("3211232345") // "(321) 123-2345"
/// formatPhone("321")        // "(321"
/// formatPhone("321123")     // "(321) 123"
/// ```
func formatPhone(_ number: String) -> String {
    let digits = number.filter { $0.isNumber }
    let limited = String(digits.prefix(10))
    
    switch limited.count {
    case 0...3:
        return limited.isEmpty ? "" : "(\(limited)"
    case 4...6:
        return "(\(limited.prefix(3))) \(limited.dropFirst(3))"
    default:
        return "(\(limited.prefix(3))) \(limited.dropFirst(3).prefix(3))-\(limited.dropFirst(6))"
    }
}
