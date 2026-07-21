"""ECDH key exchange helpers."""

from __future__ import annotations

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)

from krama.exceptions import EncryptionError

KEY_SIZE_BYTES = 32


class ECDHKeyExchange:
    """Ephemeral Curve25519 key exchange for ABDM-style data transfer."""

    @staticmethod
    def generate_key_pair() -> tuple[bytes, bytes]:
        private_key = X25519PrivateKey.generate()
        public_key = private_key.public_key()
        return (
            private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption(),
            ),
            public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            ),
        )

    @staticmethod
    def derive_shared_secret(our_private: bytes, their_public: bytes) -> bytes:
        if len(our_private) != KEY_SIZE_BYTES:
            raise EncryptionError("X25519 private key must be 32 bytes")
        if len(their_public) != KEY_SIZE_BYTES:
            raise EncryptionError("X25519 public key must be 32 bytes")

        try:
            private_key = X25519PrivateKey.from_private_bytes(our_private)
            public_key = X25519PublicKey.from_public_bytes(their_public)
            return private_key.exchange(public_key)
        except ValueError as exc:
            raise EncryptionError("Invalid X25519 key material") from exc
