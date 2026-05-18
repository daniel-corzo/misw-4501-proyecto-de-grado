//
//  PaymentPayloadNormalization.swift
//  TravelHub
//

import Foundation

enum PaymentPayloadNormalization {
    static func normalizedPAN(_ raw: String) -> String {
        raw.filter(\.isNumber)
    }

    /// Accepts ``MM/YY`` (becomes ``MM/20YY``) or ``MM/YYYY``; otherwise returns trimmed input.
    static func normalizedExpiry(_ raw: String) -> String {
        let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        let parts = trimmed.split(separator: "/", omittingEmptySubsequences: false)
        guard parts.count == 2 else { return trimmed }

        let mm = String(parts[0])
        let yyOrYyyy = String(parts[1])
        guard mm.count == 2, mm.allSatisfy(\.isNumber) else { return trimmed }

        if yyOrYyyy.count == 4, yyOrYyyy.allSatisfy(\.isNumber) {
            return trimmed
        }
        if yyOrYyyy.count == 2, yyOrYyyy.allSatisfy(\.isNumber) {
            return "\(mm)/20\(yyOrYyyy)"
        }
        return trimmed
    }
}
