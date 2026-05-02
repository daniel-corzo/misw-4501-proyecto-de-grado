//
//  RSAOAEPPaymentCipher.swift
//  TravelHub
//

import Foundation
import Security

enum PaymentCipherError: Error {
    case invalidPEM
    case keyCreationFailed
    case encryptionFailed
    case jsonEncodingFailed
}

protocol PaymentPayloadEncrypting {
    func encryptCardPayload(numero: String, cvv: String, fechaExpiracion: String) throws
        -> String
}

private struct CardPayloadInner: Encodable {
    let numero: String
    let cvv: String
    let fechaExpiracion: String

    enum CodingKeys: String, CodingKey {
        case numero
        case cvv
        case fechaExpiracion = "fecha_expiracion"
    }
}

final class RSAOAEPPaymentCipher: PaymentPayloadEncrypting {
    private let publicKey: SecKey

    init(publicKeyPEM: String) throws {
        self.publicKey = try Self.makePublicKey(fromPEM: publicKeyPEM)
    }

    func encryptCardPayload(numero: String, cvv: String, fechaExpiracion: String) throws
        -> String
    {
        let inner = CardPayloadInner(
            numero: numero,
            cvv: cvv,
            fechaExpiracion: fechaExpiracion
        )
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.sortedKeys]
        let plaintext: Data
        do {
            plaintext = try encoder.encode(inner)
        } catch {
            throw PaymentCipherError.jsonEncodingFailed
        }

        var cfError: Unmanaged<CFError>?
        guard
            let ciphertext = SecKeyCreateEncryptedData(
                publicKey,
                .rsaEncryptionOAEPSHA256,
                plaintext as CFData,
                &cfError
            ) as Data?
        else {
            throw PaymentCipherError.encryptionFailed
        }

        return ciphertext.base64EncodedString()
    }

    private static func makePublicKey(fromPEM pem: String) throws -> SecKey {
        let trimmedLines = pem.components(separatedBy: .newlines)
            .map { $0.trimmingCharacters(in: .whitespaces) }
            .filter { !$0.isEmpty }

        guard let beginLine = trimmedLines.firstIndex(where: { $0.contains("BEGIN") }),
              let endLine = trimmedLines.firstIndex(where: { $0.contains("END") }),
              endLine > beginLine
        else {
            throw PaymentCipherError.invalidPEM
        }

        let middle = trimmedLines[(beginLine + 1)..<endLine].joined()
        guard let der = Data(base64Encoded: middle, options: [.ignoreUnknownCharacters])
        else {
            throw PaymentCipherError.invalidPEM
        }

        let attributes: [String: Any] = [
            kSecAttrKeyType as String: kSecAttrKeyTypeRSA,
            kSecAttrKeyClass as String: kSecAttrKeyClassPublic,
        ]

        var cfError: Unmanaged<CFError>?
        guard let key = SecKeyCreateWithData(der as CFData, attributes as CFDictionary, &cfError)
        else {
            throw PaymentCipherError.keyCreationFailed
        }

        return key
    }
}

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
