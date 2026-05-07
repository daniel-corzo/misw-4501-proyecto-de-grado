//
//  PaymentFieldHelpers.swift
//  TravelHub
//

import Foundation

enum PaymentFieldHelpers {

    /// Strips to ASCII digits only and clamps length.
    static func digits(from raw: String, maxLen: Int) -> String {
        let d = raw.filter { $0 >= "0" && $0 <= "9" }
        guard d.count > maxLen else { return String(d) }
        return String(d.prefix(maxLen))
    }

    /// PAN groups of 4, digits only internally (caller stores digits).
    static func formatPAN(groupsOfFour digits: String) -> String {
        stride(from: 0, to: digits.count, by: 4)
            .map { i in
                let start = digits.index(digits.startIndex, offsetBy: i)
                let end = digits.index(start, offsetBy: min(4, digits.distance(from: start, to: digits.endIndex)))
                return String(digits[start ..< end])
            }
            .joined(separator: " ")
    }

    /// Display `MM` / `YY` while typing from up to four stored digits (`mmYY`).
    static func formatExpiry(mmYYdigits: String) -> String {
        let d = String(mmYYdigits.prefix(4))
        if d.count <= 2 { return d }
        let mmEnd = d.index(d.startIndex, offsetBy: 2)
        return "\(d[..<mmEnd])/\(d[mmEnd...])"
    }

    /// Expiry digits are `MMDD` interpreted as MM + YY (four digits total).
    static func isValidExpiryStartingThisMonth(mmYYdigits: String) -> Bool {
        guard mmYYdigits.count == 4,
              let mm = Int(mmYYdigits.prefix(2)),
              let yy = Int(mmYYdigits.suffix(2))
        else { return false }
        guard (1 ... 12).contains(mm) else { return false }
        let yearFull = 2000 + yy
        let cal = Calendar.current
        let now = Date()
        let curYear = cal.component(.year, from: now)
        let curMonth = cal.component(.month, from: now)
        if yearFull > curYear { return true }
        if yearFull < curYear { return false }
        return mm >= curMonth
    }
}
