//
//  String+EmailValidation.swift
//  TravelHub
//
//  Created by Andres Donoso on 20/03/26.
//

import Foundation

extension String {
    /// Validates whether the string is a properly formatted email address.
    ///
    /// This property uses a regular expression to check that the string conforms
    /// to the standard email format: `local@domain.tld`.
    ///
    /// The validation checks for:
    /// - A local part containing letters, digits, and the characters `. _ % + -`
    /// - An `@` symbol separator
    /// - A domain name containing letters, digits, and the characters `. -`
    /// - A top-level domain (TLD) of at least 2 letters
    ///
    /// - Note: This performs **format validation only**. It does not verify
    ///   whether the email address actually exists or belongs to an active mailbox.
    ///
    /// - Returns: `true` if the string matches a valid email format; `false` otherwise.
    ///
    /// ## Example
    ///
    /// ```swift
    /// "user@example.com".isValidEmail      // true
    /// "firstname.lastname@domain.org"      // true
    /// "user+tag@sub.domain.com"            // true
    ///
    /// "missingatsign.com".isValidEmail     // false
    /// "missing@tld".isValidEmail           // false
    /// "bad@@domain.com".isValidEmail       // false
    /// "".isValidEmail                      // false
    /// ```
    var isValidEmail: Bool {
        let pattern = #"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"#
        return (try? NSRegularExpression(pattern: pattern))
            .flatMap { $0.firstMatch(in: self, range: NSRange(startIndex..., in: self)) } != nil
    }
}
