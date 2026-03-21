//
//  AttributedString+Joined.swift
//  TravelHub
//
//  Created by Andres Donoso on 21/03/26.
//

import Foundation

extension [LocalizedStringResource] {
    
    /// Converts an array of `LocalizedStringResource` into a single `AttributedString`,
    /// with each element separated by the specified string.
    ///
    /// The separator is inserted **between** elements only — it is not appended
    /// after the last element.
    ///
    /// - Parameter separator: The string to insert between each localized string.
    ///
    /// - Returns: A single `AttributedString` combining all localized strings,
    ///   interleaved with the separator. Returns an empty `AttributedString`
    ///   if the array is empty.
    ///
    /// ## Example
    ///
    /// ```swift
    /// let errors: [LocalizedStringResource] = [
    ///     "error.emptyField",
    ///     "error.invalidEmail",
    ///     "error.passwordTooShort"
    /// ]
    ///
    /// let attributed = errors.toAttributedString(with: "\n")
    /// // "Field is required
    /// //  Invalid email address
    /// //  Password is too short"
    ///
    /// let inline = errors.toAttributedString(with: " • ")
    /// // "Field is required • Invalid email address • Password is too short"
    /// ```
    func joinToAttributedString(with separator: String) -> AttributedString {
        self.reduce(into: AttributedString()) { partialResult, errorText in
            if partialResult.characters.count > 0 {
                partialResult += AttributedString(separator)
            }
            
            partialResult += AttributedString(localized: errorText)
        }
    }
}
