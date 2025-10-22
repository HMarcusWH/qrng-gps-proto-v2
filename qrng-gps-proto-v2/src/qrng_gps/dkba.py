import hashlib, hmac
from typing import Optional
try:
    from Crypto.Hash import KMAC128  # pycryptodomex
    _HAS_KMAC = True
except Exception:
    _HAS_KMAC = False

from .config import TAG_LEN_BYTES as TAG_LEN

def kdf(key_material: bytes, purpose: bytes = b"") -> bytes:
    """Derive bytes via SHA3-256(key_material || purpose)."""
    h = hashlib.sha3_256()
    h.update(key_material + purpose)
    return h.digest()

def commit(epoch_index: int, sat_id: int, K: bytes) -> bytes:
    """
    Commitment C_i = SHA3-256(K_i || i || sat_id)
    """
    h = hashlib.sha3_256()
    h.update(K)
    h.update(epoch_index.to_bytes(4, "big"))
    h.update(sat_id.to_bytes(2, "big"))
    return h.digest()

def tag(nav_bytes: bytes, K: bytes) -> bytes:
    """
    Prefer KMAC128(tag_len=TAG_LEN). Fallback to truncated HMAC-SHA256.
    """
    if _HAS_KMAC:
        mac = KMAC128.new(key=K, mac_len=TAG_LEN, custom=b'NAV')
        mac.update(nav_bytes)
        return mac.digest()
    # fallback
    full = hmac.new(K, nav_bytes, hashlib.sha256).digest()
    return full[:TAG_LEN]

def verify(nav_bytes: bytes, K: bytes, tag_bytes: bytes) -> bool:
    if _HAS_KMAC:
        try:
            mac = KMAC128.new(key=K, mac_len=len(tag_bytes), custom=b'NAV')
            mac.update(nav_bytes)
            mac.verify(tag_bytes)
            return True
        except ValueError:
            return False
    expected = tag(nav_bytes, K)
    return hmac.compare_digest(expected, tag_bytes)
