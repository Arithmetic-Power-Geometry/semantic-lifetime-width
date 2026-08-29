from __future__ import annotations
from dataclasses import dataclass
from math import ceil, log2


@dataclass(frozen=True)
class LifetimeSchedule:
    """Certified birth/retirement intervals for a factorizable binary history."""
    births: tuple[int, ...]
    deaths: tuple[int, ...]

    def __post_init__(self):
        if len(self.births) != len(self.deaths):
            raise ValueError("births and deaths must have equal length")
        for b, d in zip(self.births, self.deaths):
            if b < 0 or d <= b:
                raise ValueError("each distinction must satisfy 0 <= birth < death")

    @property
    def n_distinctions(self) -> int:
        return len(self.births)

    @property
    def horizon(self) -> int:
        return max(self.deaths, default=0)


def slw_from_class_count(n_classes: int) -> int:
    """Bits required to identify one query-relative future-equivalence class."""
    if n_classes < 1:
        raise ValueError("n_classes must be positive")
    return 0 if n_classes == 1 else ceil(log2(n_classes))


def live_counts(schedule: LifetimeSchedule) -> list[int]:
    """Number of independently unexpired binary distinctions at each stage."""
    return [
        sum(b <= t < d for b, d in zip(schedule.births, schedule.deaths))
        for t in range(schedule.horizon)
    ]


def quotient_class_counts(schedule: LifetimeSchedule, core_states: int = 1) -> list[int]:
    """Upper-bound/exact class counts for the factorizable schedule model.

    In this companion construction, a quotient representative is determined by one
    core label and a valuation of every independently unexpired distinction.
    """
    if core_states < 1:
        raise ValueError("core_states must be positive")
    return [core_states * (2**a) for a in live_counts(schedule)]


def semantic_lifetime_width(schedule: LifetimeSchedule, core_states: int = 1) -> int:
    counts = quotient_class_counts(schedule, core_states=core_states)
    return max((slw_from_class_count(c) for c in counts), default=0)


def linear_preservation_volume(schedule: LifetimeSchedule) -> int:
    """V_Q^lin = sum_t |L_Q(t)| for a factorizable distinction system."""
    return sum(live_counts(schedule))


def preservation_volume(schedule: LifetimeSchedule) -> int:
    """Backward-compatible alias for linear_preservation_volume."""
    return linear_preservation_volume(schedule)


def lifetime_sum(schedule: LifetimeSchedule) -> int:
    """Equivalent double-counting form sum_d (death-birth)."""
    return sum(d - b for b, d in zip(schedule.births, schedule.deaths))


def semantic_state_volume(schedule: LifetimeSchedule, core_states: int = 1) -> int:
    """V_Q^state = sum_t q_t 2^{|L_Q(t)|}, with constant q_t here."""
    return sum(quotient_class_counts(schedule, core_states=core_states))


def fixed_state_volume(schedule: LifetimeSchedule, core_states: int = 1) -> int:
    """Counterfactual volume if every created distinction is preserved forever."""
    if core_states < 1:
        raise ValueError("core_states must be positive")
    if schedule.horizon == 0:
        return 0
    created_by_t = [sum(b <= t for b in schedule.births) for t in range(schedule.horizon)]
    return sum(core_states * (2**a) for a in created_by_t)


def expiring_block_schedule(stages: int, block_size: int, lifetime: int = 1) -> LifetimeSchedule:
    if stages < 1 or block_size < 1 or lifetime < 1:
        raise ValueError("stages, block_size, lifetime must be positive")
    births, deaths = [], []
    for t in range(stages):
        for _ in range(block_size):
            births.append(t)
            deaths.append(t + lifetime)
    return LifetimeSchedule(tuple(births), tuple(deaths))


def clique_parity_metrics(n: int) -> dict:
    """Complete-graph structure with parity query.

    Prefix histories have exactly two query-relative future classes: accumulated
    parity 0 and accumulated parity 1. Hence SLW=ceil(log2 2)=1.
    """
    if n < 2:
        raise ValueError("n must be >=2")
    return {
        "n": n,
        "pathwidth": n - 1,
        "future_classes": 2,
        "slw": slw_from_class_count(2),
        "query": "parity",
    }


def path_index_metrics(n: int) -> dict:
    """Path-like input with delayed indexed-bit query.

    Before the index is revealed, all 2^n strings have distinct future behavior.
    """
    if n < 2:
        raise ValueError("n must be >=2")
    classes = 2**n
    return {
        "n": n,
        "pathwidth": 1,
        "future_classes": classes,
        "slw": slw_from_class_count(classes),
        "query": "indexed-bit",
    }


def same_structure_query_metrics(n: int) -> list[dict]:
    if n < 2:
        raise ValueError("n must be >=2")
    return [
        {
            "n": n,
            "structure": "sequential-input",
            "query": "parity",
            "future_classes": 2,
            "slw": 1,
            "output_bits": 1,
        },
        {
            "n": n,
            "structure": "sequential-input",
            "query": "indexed-bit",
            "future_classes": 2**n,
            "slw": n,
            "output_bits": 1,
        },
    ]


def bounded_slw_state_bound(n: int, slw: int, poly_degree: int = 2) -> int:
    """Illustrative theorem-bound factor n^d * 2^SLW."""
    if n < 1 or slw < 0 or poly_degree < 0:
        raise ValueError
    return (n**poly_degree) * (2**slw)


def log2_ratio(a: int, b: int) -> float:
    if a <= 0 or b <= 0:
        raise ValueError("positive inputs required")
    return log2(a) - log2(b)
