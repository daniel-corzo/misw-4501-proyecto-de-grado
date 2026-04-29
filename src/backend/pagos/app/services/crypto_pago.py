"""Descifrado RSA-OAEP (clave publica cliente, privada servidor)."""

import base64

from cryptography.exceptions import InvalidKey
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key


class DecifradoTarjetaError(Exception):
    """Error al procesar ciphertext o PEM."""


def descifrar_payload_rsa_base64(pem_pkcs8_rsa_privada: str, payload_b64: str) -> bytes:
    """
    Descifrar blob Base64 producido como RSA-OAEP(SHA-256/MGF-SHA256) sobre bytes UTF-8 del JSON PCI.
    """
    try:
        data = base64.b64decode(payload_b64.strip(), validate=False)
    except Exception as exc:
        raise DecifradoTarjetaError("Payload cifrado invalido") from exc

    try:
        private_key = load_pem_private_key(
            pem_pkcs8_rsa_privada.encode(),
            password=None,
        )
    except (ValueError, InvalidKey, TypeError) as exc:
        raise DecifradoTarjetaError("Llave RSA de servidor invalida") from exc

    try:
        return private_key.decrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
    except Exception as exc:
        raise DecifradoTarjetaError("No fue posible procesar datos de tarjeta") from exc


def ultimos_cuatro_digitos(numero_tarjeta: str) -> str:
    digits = "".join(c for c in numero_tarjeta if c.isdigit())
    if len(digits) < 4:
        raise ValueError("PAN demasiado corto")
    return digits[-4:]

