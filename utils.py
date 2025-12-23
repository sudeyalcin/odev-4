from __future__ import annotations
from typing import List
import numpy as np

def route_length(route: List[int], dist: np.ndarray) -> float:
    """Compute total tour length for a TSP tour that starts at route[0] and returns to start."""
    total = 0.0
    for i in range(len(route) - 1):
        total += float(dist[route[i], route[i + 1]])
    total += float(dist[route[-1], route[0]])
    return total

def safe_inverse_distance(dist: np.ndarray, eps: float = 1e-9) -> np.ndarray:
    """Heuristic matrix eta = 1/(dist + eps) with zeros on diagonal."""
    inv = 1.0 / (dist + eps)
    np.fill_diagonal(inv, 0.0)
    return inv
