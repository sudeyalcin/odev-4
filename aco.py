from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
from .utils import route_length, safe_inverse_distance

@dataclass
class ACOParams:
    ants: int = 40
    iterations: int = 150
    alpha: float = 1.0          # pheromone influence
    beta: float = 3.0           # heuristic influence
    rho: float = 0.35           # evaporation rate (0..1)
    q: float = 100.0            # pheromone deposit constant
    seed: int = 42

def _select_next(rng: np.random.Generator, probs: np.ndarray, candidates: np.ndarray) -> int:
    probs = probs / probs.sum()
    return int(rng.choice(candidates, p=probs))

def solve_tsp_aco(dist: np.ndarray, params: ACOParams, start: int = 0) -> Tuple[List[int], float, List[float]]:
    """
    Ant Colony Optimization for TSP using a distance matrix.
    Returns: (best_route, best_length, best_history)
    """
    if dist.ndim != 2 or dist.shape[0] != dist.shape[1]:
        raise ValueError("dist must be a square matrix")

    n = dist.shape[0]
    if n < 2:
        return [0], 0.0, [0.0]

    rng = np.random.default_rng(params.seed)

    # initialize pheromone
    tau = np.ones((n, n), dtype=float)
    np.fill_diagonal(tau, 0.0)

    eta = safe_inverse_distance(dist)

    best_route: List[int] = []
    best_len = float("inf")
    history: List[float] = []

    nodes = np.arange(n)

    for it in range(params.iterations):
        all_routes = []
        all_lens = []

        for _ in range(params.ants):
            visited = np.zeros(n, dtype=bool)
            route = [start]
            visited[start] = True

            current = start
            for _step in range(n - 1):
                candidates = nodes[~visited]
                # probability proportional to tau^alpha * eta^beta
                desirability = (tau[current, candidates] ** params.alpha) * (eta[current, candidates] ** params.beta)
                # handle numerical corner case
                if desirability.sum() <= 0:
                    nxt = int(rng.choice(candidates))
                else:
                    nxt = _select_next(rng, desirability, candidates)
                route.append(nxt)
                visited[nxt] = True
                current = nxt

            length = route_length(route, dist)
            all_routes.append(route)
            all_lens.append(length)

            if length < best_len:
                best_len = length
                best_route = route

        # evaporate
        tau *= (1.0 - params.rho)

        # deposit pheromone (elitist: deposit from best of this iteration)
        best_idx = int(np.argmin(all_lens))
        iter_best_route = all_routes[best_idx]
        iter_best_len = all_lens[best_idx]
        deposit = params.q / max(iter_best_len, 1e-9)

        for i in range(n - 1):
            a, b = iter_best_route[i], iter_best_route[i + 1]
            tau[a, b] += deposit
            tau[b, a] += deposit
        # close the tour
        a, b = iter_best_route[-1], iter_best_route[0]
        tau[a, b] += deposit
        tau[b, a] += deposit

        history.append(best_len)

    return best_route, best_len, history
