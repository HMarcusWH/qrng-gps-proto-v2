from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from .overlay import EpochMsg
import copy

@dataclass
class Meaconer:
    """
    Simple meaconer that replays messages with a fixed epoch delay and level.
    """
    delay_epochs: int = 2
    active: bool = True

    def process(self, stream: List[EpochMsg]) -> List[EpochMsg]:
        if not self.active or self.delay_epochs <= 0:
            return stream
        out = []
        for m in stream:
            dm = copy.deepcopy(m)
            dm.i = m.i + self.delay_epochs  # appears later
            out.append(dm)
        return out
