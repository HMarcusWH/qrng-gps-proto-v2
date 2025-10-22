from typing import Dict
from .config import RISK_ESC_WEIGHT, RISK_SPREAD_WEIGHT, RISK_GEO_WEIGHT
from .geo_residuals import tdoa_residuals

def fuse(auth_epochs: Dict[int, int], esc_scores: Dict[int, float]) -> Dict[str, float]:
    """
    Return a dict with risk components and total:
      - spread: epoch index spread across satellites
      - esc: sum of ESC residuals
      - geo: geometric/TDoA residual proxy
      - total: weighted sum
    """
    if not auth_epochs:
        return dict(spread=0.0, esc=0.0, geo=0.0, total=0.0)

    epochs = list(auth_epochs.values())
    spread = float(max(epochs) - min(epochs))
    esc_sum = float(sum(esc_scores.get(s, 0.0) for s in auth_epochs.keys()))
    geo = float(tdoa_residuals(auth_epochs))
    total = min(100.0, RISK_SPREAD_WEIGHT * spread + RISK_ESC_WEIGHT * esc_sum + RISK_GEO_WEIGHT * geo)
    return dict(spread=spread, esc=esc_sum, geo=geo, total=total)
