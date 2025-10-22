# QRNG-GPS Prototype (DKBA + ESC overlay)

A minimal, runnable **prototype** of the QRNG-anchored GPS/GNSS authentication concept.
It implements:
- Delayed-Key Broadcast Authentication (DKBA) with HMAC tags and SHA3 commitments
- Ephemeral spreading-code metadata (ESC) stubs + post-disclosure check
- Meaconing (replay) simulation and simple residual fusion to raise a SpoofRisk score
- A toy end-to-end demo over a few satellites and epochs

> This is **lab code** for concept demonstration. It is not a GNSS signal generator.

## Quickstart

```bash
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run_demo.py
pytest -q
```

Expected output shows per-epoch authentication results and a final risk summary;
one satellite is configured to be "meaconed" (delayed), which should be detected
after key disclosure.

## Layout

```
qrng-gps-proto/
  src/qrng_gps/
    __init__.py
    dkba.py
    overlay.py
    esc_meta.py
    meacon_detect.py
    pqc_anchor.py
    qrng_source.py
    receiver_verify.py
    sim_channel.py
    logfmt.py
  tests/
    test_dkba.py
    test_overlay.py
    test_meacon.py
  run_demo.py
  requirements.txt
  LICENSE
  .gitignore
  README.md
```

## Notes

- This prototype uses **HMAC-SHA256 (truncated)** for tags to avoid heavy deps.
  Swap to KMAC/SHA3 or POLYVAL-based MAC for production.
- PQC anchoring is stubbed. Replace with liboqs or a PQC library to sign the
  rolling commitment root in a real system.
- No RF is generated here. For SDR/HIL, insert `overlay.encode(...)` payloads
  into a baseband pipeline in a shielded/lawful lab setup.

## Safety & Legal

Do **not** transmit on L1/L2/L5 over the air. Use cabled or shielded-chamber
setups only and obey local regulations.
