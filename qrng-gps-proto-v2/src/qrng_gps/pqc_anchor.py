"""
PQC anchoring with optional liboqs; falls back to a SHA3 placeholder if oqs not available.
"""
import hashlib
try:
    import oqs  # type: ignore
    _HAS_OQS = True
except Exception:
    _HAS_OQS = False

_ALG = "Dilithium2"

class PQCSigner:
    def __init__(self):
        if _HAS_OQS:
            self._sig = oqs.Signature(_ALG)
            self._sk = self._sig.generate_keypair()
            self._pk = self._sig.export_public_key()
        else:
            self._sig = None
            self._sk = b"STUB_SK"
            self._pk = b"STUB_PK"

    @property
    def public_key(self) -> bytes:
        return self._pk

    def sign_root(self, root_bytes: bytes) -> bytes:
        if _HAS_OQS:
            return self._sig.sign(root_bytes)
        # fallback: SHA3 tag with constant to mark stub
        return hashlib.sha3_256(root_bytes + b"PQC_STUB").digest()

    def verify_root(self, root_bytes: bytes, sig: bytes) -> bool:
        if _HAS_OQS:
            with oqs.Signature(_ALG) as verifier:
                return verifier.verify(root_bytes, sig, self._pk)
        return self.sign_root(root_bytes) == sig
