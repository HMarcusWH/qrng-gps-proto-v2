from typing import Dict

def tdoa_residuals(auth_epochs: Dict[int, int]) -> float:
    """
    Placeholder geometric check:
    - Use the spread in authenticated epoch indices as a proxy for inconsistent timing.
    Real system would compute TDoA against geometry; here we just return spread.
    """
    if not auth_epochs:
        return 0.0
    epochs = list(auth_epochs.values())
    return float(max(epochs) - min(epochs))
