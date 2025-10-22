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
        self._path = Path(path) if path else None
        self._f = open(self._path, "rb") if self._path else None

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
            self._f = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    def __del__(self):
        self.close()
