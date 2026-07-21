"""AES-GCM encryption helpers."""

from __future__ import annotations

import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from krama.exceptions import EncryptionError

AES_KEY_SIZE_BYTES = 32
NONCE_SIZE_BYTES = 12


class AESGCMCipher:
    """AES-256-GCM encryption and decryption."""

    @staticmethod
    def derive_key(shared_secret: bytes, salt: bytes | None = None) -> bytes:
        if len(shared_secret) < AES_KEY_SIZE_BYTES:
            raise EncryptionError("shared_secret must be at least 32 bytes")
        return HKDF(
            algorithm=hashes.SHA256(),
            length=AES_KEY_SIZE_BYTES,
            salt=salt,
            info=b"krama-core-abdm-data-transfer",
        ).derive(shared_secret)

    @staticmethod
    def encrypt(
        data: bytes,
        key: bytes,
        nonce: bytes | None = None,
        associated_data: bytes | None = None,
    ) -> tuple[bytes, bytes]:
        AESGCMCipher._validate_key(key)
        if nonce is None:
            nonce = os.urandom(NONCE_SIZE_BYTES)
        AESGCMCipher._validate_nonce(nonce)

        ciphertext = AESGCM(key).encrypt(nonce, data, associated_data)
        return ciphertext, nonce

    @staticmethod
    def decrypt(
        ciphertext: bytes,
        key: bytes,
        nonce: bytes,
        associated_data: bytes | None = None,
    ) -> bytes:
        AESGCMCipher._validate_key(key)
        AESGCMCipher._validate_nonce(nonce)
        try:
            return AESGCM(key).decrypt(nonce, ciphertext, associated_data)
        except InvalidTag as exc:
            raise EncryptionError("AES-GCM authentication failed") from exc

    @staticmethod
    def _validate_key(key: bytes) -> None:
        if len(key) != AES_KEY_SIZE_BYTES:
            raise EncryptionError("AES-GCM key must be 32 bytes")

    @staticmethod
    def _validate_nonce(nonce: bytes) -> None:
        if len(nonce) != NONCE_SIZE_BYTES:
            raise EncryptionError("AES-GCM nonce must be 12 bytes")
