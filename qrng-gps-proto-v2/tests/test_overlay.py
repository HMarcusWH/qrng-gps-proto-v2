from qrng_gps.overlay import EpochMsg, encode, decode
def test_encode_decode_roundtrip():
    m = EpochMsg(i=3, sat_id=12, nav=b"\x00\x01", C_i=b"\x02"*32, A_prev=None, K_disclose_prev=None, esc_meta={"family":"GOLD"})
    buf = encode(m)
    m2 = decode(buf)
    assert m2.i == m.i and m2.sat_id == m.sat_id
    assert m2.nav == m.nav and m2.C_i == m.C_i
    assert m2.esc_meta["family"] == "GOLD"
