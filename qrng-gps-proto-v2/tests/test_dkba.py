from qrng_gps import dkba
def test_commit_and_tag_roundtrip():
    K = b"\x01"*32
    nav = b"hello world"
    C = dkba.commit(7, 42, K)
    assert isinstance(C, bytes) and len(C) == 32
    t = dkba.tag(nav, K)
    assert dkba.verify(nav, K, t)
    assert not dkba.verify(nav+b"!", K, t)
