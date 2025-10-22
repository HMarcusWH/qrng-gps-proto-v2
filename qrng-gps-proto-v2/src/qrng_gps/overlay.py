from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import json, binascii

@dataclass
class EpochMsg:
    i: int
    sat_id: int
    nav: bytes
    C_i: bytes
    A_prev: Optional[bytes] = None
    K_disclose_prev: Optional[bytes] = None
    esc_meta: Optional[Dict[str, Any]] = None

def _hex_or_none(b: Optional[bytes]) -> Optional[str]:
    return b.hex() if b is not None else None

def encode(m: EpochMsg) -> bytes:
    obj = {
        "i": m.i,
        "sid": m.sat_id,
        "nav": m.nav.hex(),
        "C": m.C_i.hex(),
        "A": _hex_or_none(m.A_prev),
        "Kprev": _hex_or_none(m.K_disclose_prev),
        "esc": m.esc_meta or {}
    }
    return json.dumps(obj, separators=(",", ":")).encode()

def decode(buf: bytes) -> EpochMsg:
    o = json.loads(buf.decode())
    return EpochMsg(
        i=o["i"],
        sat_id=o["sid"],
        nav=bytes.fromhex(o["nav"]),
        C_i=bytes.fromhex(o["C"]),
        A_prev=bytes.fromhex(o["A"]) if o["A"] else None,
        K_disclose_prev=bytes.fromhex(o["Kprev"]) if o["Kprev"] else None,
        esc_meta=o.get("esc", {})
    )
