import pytest

from krama.crypto import AESGCMCipher, ECDHKeyExchange
from krama.exceptions import EncryptionError


def test_ecdh_key_exchange_derives_same_secret_on_both_sides():
    alice_private, alice_public = ECDHKeyExchange.generate_key_pair()
    bob_private, bob_public = ECDHKeyExchange.generate_key_pair()

    alice_secret = ECDHKeyExchange.derive_shared_secret(alice_private, bob_public)
    bob_secret = ECDHKeyExchange.derive_shared_secret(bob_private, alice_public)

    assert len(alice_private) == 32
    assert len(alice_public) == 32
    assert alice_secret == bob_secret
    assert len(alice_secret) == 32


def test_ecdh_rejects_invalid_key_lengths():
    private_key, public_key = ECDHKeyExchange.generate_key_pair()

    with pytest.raises(EncryptionError, match="private key"):
        ECDHKeyExchange.derive_shared_secret(private_key[:-1], public_key)

    with pytest.raises(EncryptionError, match="public key"):
        ECDHKeyExchange.derive_shared_secret(private_key, public_key[:-1])


def test_ecdh_wraps_invalid_key_material():
    private_key, _public_key = ECDHKeyExchange.generate_key_pair()

    with pytest.raises(EncryptionError, match="Invalid X25519"):
        ECDHKeyExchange.derive_shared_secret(private_key, bytes(32))


def test_aes_gcm_derive_key_is_deterministic_with_same_salt():
    secret = b"s" * 32
    salt = b"salt"

    key_one = AESGCMCipher.derive_key(secret, salt=salt)
    key_two = AESGCMCipher.derive_key(secret, salt=salt)

    assert key_one == key_two
    assert len(key_one) == 32


def test_aes_gcm_derive_key_rejects_short_secret():
    with pytest.raises(EncryptionError, match="shared_secret"):
        AESGCMCipher.derive_key(b"short")


def test_aes_gcm_encrypt_decrypt_roundtrip_with_explicit_nonce():
    key = AESGCMCipher.derive_key(b"k" * 32)
    nonce = b"n" * 12
    plaintext = b'{"resourceType":"Bundle"}'
    associated_data = b"krama-test"

    ciphertext, returned_nonce = AESGCMCipher.encrypt(
        plaintext,
        key,
        nonce=nonce,
        associated_data=associated_data,
    )
    decrypted = AESGCMCipher.decrypt(
        ciphertext,
        key,
        returned_nonce,
        associated_data=associated_data,
    )

    assert returned_nonce == nonce
    assert ciphertext != plaintext
    assert decrypted == plaintext


def test_aes_gcm_encrypt_generates_nonce_when_absent():
    key = AESGCMCipher.derive_key(b"k" * 32)

    ciphertext, nonce = AESGCMCipher.encrypt(b"hello", key)

    assert len(nonce) == 12
    assert AESGCMCipher.decrypt(ciphertext, key, nonce) == b"hello"


def test_aes_gcm_rejects_invalid_key_and_nonce_lengths():
    valid_key = AESGCMCipher.derive_key(b"k" * 32)

    with pytest.raises(EncryptionError, match="key"):
        AESGCMCipher.encrypt(b"data", b"short", nonce=b"n" * 12)

    with pytest.raises(EncryptionError, match="nonce"):
        AESGCMCipher.encrypt(b"data", valid_key, nonce=b"short")

    with pytest.raises(EncryptionError, match="key"):
        AESGCMCipher.decrypt(b"data", b"short", b"n" * 12)

    with pytest.raises(EncryptionError, match="nonce"):
        AESGCMCipher.decrypt(b"data", valid_key, b"short")


def test_aes_gcm_rejects_tampered_ciphertext():
    key = AESGCMCipher.derive_key(b"k" * 32)
    ciphertext, nonce = AESGCMCipher.encrypt(b"hello", key, nonce=b"n" * 12)
    tampered = ciphertext[:-1] + bytes([ciphertext[-1] ^ 1])

    with pytest.raises(EncryptionError, match="authentication failed"):
        AESGCMCipher.decrypt(tampered, key, nonce)
