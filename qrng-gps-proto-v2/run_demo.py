import argparse
from dataclasses import dataclass
from typing import Dict, List, Optional
from qrng_gps.qrng_source import QRNG
from qrng_gps import dkba, overlay, esc_meta, meacon_detect
from qrng_gps.receiver_verify import Verifier
from qrng_gps.sim_channel import Meaconer
from qrng_gps.config import EPOCH_SECONDS

@dataclass
class SatState:
    sat_id: int
    K: Dict[int, bytes]
    nav: Dict[int, bytes]
    esc: Dict[int, dict]

def make_sats(num_sats: int = 4, epochs: int = 8, rng: Optional[QRNG] = None) -> Dict[int, SatState]:
    owns_rng = False
    if rng is None:
        rng = QRNG()
        owns_rng = True

    try:
        sats = {}
        for sid in range(1, num_sats + 1):
            K = {}
            nav = {}
            escd = {}
            for i in range(epochs):
                Ki = rng.get_bits(32)
                K[i] = Ki
                nav[i] = rng.get_bits(120)
                escd[i] = esc_meta.derive_esc_meta(Ki)
            sats[sid] = SatState(sat_id=sid, K=K, nav=nav, esc=escd)
        return sats
    finally:
        if owns_rng:
            rng.close()

def trace_provider_factory(meaconed_sid: int, delay_epochs: int):
    def provider(sat_id: int, i: int):
        if sat_id == meaconed_sid and i >= delay_epochs:
            return {"family_obs":"GOLD","ppm_obs":999,"phase_mchips_obs":999}
        return {"family_obs":None,"ppm_obs":0,"phase_mchips_obs":0}
    return provider

def main():
    ap = argparse.ArgumentParser(description="QRNG-GPS DKBA+ESC demo")
    ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--sats", type=int, default=4)
    ap.add_argument("--meacon-sid", type=int, default=2)
    ap.add_argument("--delay", type=int, default=2, help="meacon delay (epochs)")
    ap.add_argument("--qrng-path", type=str, default=None, help="path to QRNG entropy file")
    args = ap.parse_args()

    with QRNG(args.qrng_path) as rng:
        sats = make_sats(num_sats=args.sats, epochs=args.epochs, rng=rng)

    streams: Dict[int, List[overlay.EpochMsg]] = {}
    for sid, st in sats.items():
        stream = []
        for i in range(args.epochs):
            C_i = dkba.commit(i, sid, st.K[i])
            A_prev = dkba.tag(st.nav[i-1], st.K[i-1]) if i > 0 else None
            K_disclose_prev = st.K[i-1] if i > 0 else None
            m = overlay.EpochMsg(i=i, sat_id=sid, nav=st.nav[i], C_i=C_i,
                                  A_prev=A_prev, K_disclose_prev=K_disclose_prev, esc_meta=st.esc[i])
            stream.append(m)
        streams[sid] = stream

    meaconed_sid = args.meacon_sid
    delay = args.delay
    meaconer = Meaconer(delay_epochs=delay, active=True)
    meaconed_stream = meaconer.process(streams[meaconed_sid])

    verifier = Verifier(esc_trace_provider=trace_provider_factory(meaconed_sid, delay))

    print("== Running demo ==")
    for i in range(args.epochs + delay):
        for sid in range(1, args.sats+1):
            src = meaconed_stream if sid == meaconed_sid else streams[sid]
            ms = [m for m in src if m.i == i]
            for m in ms:
                state = verifier.ingest(m)
                label = {0:"PENDING", 1:"VALID", 2:"SUSPECT"}[state]
                print(f"recv sat {m.sat_id} epoch {m.i}: {label}")

        risk = meacon_detect.fuse(verifier.auth_epochs, verifier.esc_scores)
        if risk["total"] > 0:
            print(f"[step {i}] SpoofRisk={risk['total']:.1f}  (spread={risk['spread']:.1f}, esc={risk['esc']:.1f}, geo={risk['geo']:.1f}) "
                  f"auth_epochs={verifier.auth_epochs}")

    print("\n== Final summary ==")
    print(f"Latest authenticated epochs: {verifier.auth_epochs}")
    risk = meacon_detect.fuse(verifier.auth_epochs, verifier.esc_scores)
    print(f"Final SpoofRisk={risk['total']:.1f}  (spread={risk['spread']:.1f}, esc={risk['esc']:.1f}, geo={risk['geo']:.1f})")
    print(f"Assumed epoch length: {EPOCH_SECONDS}s")

if __name__ == "__main__":
    main()
