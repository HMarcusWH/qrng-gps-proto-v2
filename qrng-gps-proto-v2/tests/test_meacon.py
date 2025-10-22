from qrng_gps.meacon_detect import fuse

def test_fuse_scoring():
    auth = {1:10, 2:10, 3:10, 4:10}
    resids = {1:0.0, 2:0.0, 3:0.0, 4:0.0}
    assert fuse(auth, resids) == 0.0
    auth2 = {1:12, 2:10, 3:15, 4:9}
    score = fuse(auth2, resids)
    assert score > 0.0
