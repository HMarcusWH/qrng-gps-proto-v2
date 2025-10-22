from qrng_gps.meacon_detect import fuse


def test_fuse_returns_components():
    auth = {1: 10, 2: 10, 3: 10, 4: 10}
    resids = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
    risk = fuse(auth, resids)
    assert risk == {"spread": 0.0, "esc": 0.0, "geo": 0.0, "total": 0.0}


def test_fuse_combines_weights_without_capping():
    auth = {1: 10, 2: 11, 3: 12, 4: 13}
    resids = {1: 1.0, 2: 2.0, 3: 3.0, 4: 4.0}
    risk = fuse(auth, resids)
    # spread and geo are both the max/min difference which is 3
    assert risk["spread"] == 3.0
    assert risk["geo"] == 3.0
    # ESC component sums the provided residuals
    assert risk["esc"] == 10.0
    # Weighted sum = (20 * 3) + (0.5 * 10) + (1 * 3) = 68
    assert risk["total"] == 68.0


def test_fuse_caps_at_100():
    auth = {1: 9, 2: 10, 3: 15, 4: 12}
    resids = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
    risk = fuse(auth, resids)
    assert risk["total"] == 100.0
