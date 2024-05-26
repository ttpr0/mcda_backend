from typing import Protocol

from access_api.decay import get_distance_decay

class IDistanceDecay(Protocol):
    def get_distance_weight(self, distance: int) -> float:
        """
        Computes the decayed weight (range [0, 1]) for the given distance.
        """
        ...
    
    def get_max_distance(self) -> int:
        """
        Maximum distance to give distance-weight greater than 0.
        """
        ...

def get_dummy_decay(decay: dict) -> IDistanceDecay:
    d = get_distance_decay(decay)
    if d is None:
        raise ValueError(f"Invalid decay parameters {decay}.")
    return d

def get_max_distance(decay: dict) -> int:
    if "max_range" in decay:
        return int(decay["max_range"])
    if "ranges" in decay:
        return int(decay["ranges"][-1])
    raise ValueError(f"Invalid decay parameters {decay}.")
