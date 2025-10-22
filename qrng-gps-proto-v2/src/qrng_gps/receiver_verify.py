from collections import defaultdict
from typing import Dict, Tuple, Optional
from .dkba import commit, verify
from .esc_meta import posthoc_check

PENDING, VALID, SUSPECT = 0, 1, 2

class Verifier:
    def __init__(self, esc_trace_provider=None):
        # buf[sat_id][i] = (nav, C, A, esc_meta)
        self.buf = defaultdict(dict)
        self.auth_epochs: Dict[int, int] = {}      # sat_id -> latest authenticated epoch
        self.esc_scores: Dict[int, float] = {}     # sat_id -> last residual norm
        self.esc_trace_provider = esc_trace_provider

    def ingest(self, m) -> int:
        self.buf[m.sat_id][m.i] = (m.nav, m.C_i, m.A_prev, m.esc_meta)
        # If this message discloses K for previous epoch, try to authenticate it now.
        if m.K_disclose_prev is not None:
            return self._authenticate(m.sat_id, m.i - 1, m.K_disclose_prev)
        return PENDING

    def disclose(self, sat_id: int, i: int, K: bytes) -> int:
        return self._authenticate(sat_id, i, K)

    def _authenticate(self, sat_id: int, i: int, K: bytes) -> int:
        b = self.buf[sat_id].get(i)
        if not b:
            return SUSPECT
        nav, C, A, esc_meta = b
        ok_c = (commit(i, sat_id, K) == C)
        ok_a = True if A is None else verify(nav, K, A)
        if ok_c and ok_a:
            self.auth_epochs[sat_id] = max(i, self.auth_epochs.get(sat_id, -1))
            # post-disclosure ESC check (use trace provider if available)
            if self.esc_trace_provider and esc_meta:
                trace = self.esc_trace_provider(sat_id, i)
                r = posthoc_check(trace, esc_meta)
                self.esc_scores[sat_id] = abs(r["ppm_resid"]) + abs(r["phase_resid"]) + r["family_penalty"]
            return VALID
        return SUSPECT
