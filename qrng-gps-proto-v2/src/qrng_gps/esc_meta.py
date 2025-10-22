from typing import Dict, Any
import struct, hashlib

FAMILIES = ["GOLD", "KASAMI", "LEGENDRE", "WEIL", "MIXED"]

def derive_esc_meta(Ki: bytes) -> Dict[str, Any]:
    """
    Derive ephemeral spreading-code settings from Ki deterministically.
    """
    h = hashlib.sha3_256(Ki + b"ESC").digest()
    fam_idx = h[0] % len(FAMILIES)
    # small bounded dithers
    ppm = (int.from_bytes(h[1:3], "big") % 101) - 50   # [-50, +50] ppm
    phase_mchips = (h[3] % 201) - 100                  # [-100, +100] milli-chips
    return {"family": FAMILIES[fam_idx], "ppm": ppm, "phase_mchips": phase_mchips}

def posthoc_check(trace: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, float]:
    """
    Compare recorded trace features vs disclosed meta. In real RF this would
    run correlator re-alignment. Here we compute simple residuals.
    """
    r_ppm = abs(float(trace.get("ppm_obs", 0)) - float(meta.get("ppm", 0)))
    r_phase = abs(float(trace.get("phase_mchips_obs", 0)) - float(meta.get("phase_mchips", 0)))
    # family mismatch counts heavy
    r_family = 0.0 if trace.get("family_obs") == meta.get("family") else 100.0
    return {"ppm_resid": r_ppm, "phase_resid": r_phase, "family_penalty": r_family}
