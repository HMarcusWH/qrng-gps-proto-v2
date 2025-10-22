import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from run_demo import make_sats
from qrng_gps.qrng_source import QRNG


def test_qrng_context_manager_closes_file(tmp_path):
    entropy_path = tmp_path / "entropy.bin"
    entropy_path.write_bytes(b"0123456789")

    with QRNG(str(entropy_path)) as rng:
        chunk = rng.get_bits(4)
        assert chunk == b"0123"

    # After exiting the context, the file handle should be closed/reset
    assert getattr(rng, "_f") is None


def test_make_sats_consumes_qrng_bytes(tmp_path):
    entropy_path = tmp_path / "entropy.bin"
    data = bytes((i % 256 for i in range(400)))
    entropy_path.write_bytes(data)

    with QRNG(str(entropy_path)) as rng:
        sats = make_sats(num_sats=1, epochs=2, rng=rng)

    sat = sats[1]
    assert sat.K[0] == data[0:32]
    assert sat.nav[0] == data[32:152]
    assert sat.K[1] == data[152:184]
    assert sat.nav[1] == data[184:304]
