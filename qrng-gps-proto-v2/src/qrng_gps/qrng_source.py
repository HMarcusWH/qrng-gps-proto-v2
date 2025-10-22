import os
from pathlib import Path
from typing import Optional

class QRNG:
    """
    Simple QRNG adapter.
    - If a file path is provided, bytes are read from it and looped.
    - Otherwise, os.urandom is used (placeholder for a real QRNG device).
    """
    def __init__(self, path: Optional[str] = None):
        self._f = open(path, "rb") if path else None

    def get_bits(self, n: int) -> bytes:
        if self._f:
            b = self._f.read(n)
            if len(b) < n:
                self._f.seek(0)
                b += self._f.read(n - len(b))
            return b
        return os.urandom(n)

    def close(self):
        if self._f:
            self._f.close()
