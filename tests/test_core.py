from slw.core import (
    expiring_block_schedule,
    live_counts,
    semantic_lifetime_width,
    linear_preservation_volume,
    lifetime_sum,
    semantic_state_volume,
    fixed_state_volume,
    clique_parity_metrics,
    path_index_metrics,
    slw_from_class_count,
    quotient_class_counts,
)


def test_lifetime_accounting():
    s = expiring_block_schedule(10, 3, 2)
    assert linear_preservation_volume(s) == lifetime_sum(s)


def test_quotient_slw_definition():
    assert slw_from_class_count(1) == 0
    assert slw_from_class_count(2) == 1
    assert slw_from_class_count(8) == 3
    assert slw_from_class_count(9) == 4


def test_separating_families():
    assert clique_parity_metrics(20)["pathwidth"] == 19
    assert clique_parity_metrics(20)["future_classes"] == 2
    assert clique_parity_metrics(20)["slw"] == 1
    assert path_index_metrics(20)["pathwidth"] == 1
    assert path_index_metrics(20)["future_classes"] == 2**20
    assert path_index_metrics(20)["slw"] == 20


def test_state_volume_and_core_factor():
    s = expiring_block_schedule(8, 2, 1)
    assert semantic_lifetime_width(s) == 2
    assert semantic_lifetime_width(s, core_states=3) == 4  # ceil(log2(3*4))
    assert semantic_state_volume(s, core_states=3) == sum(quotient_class_counts(s, 3))
    assert fixed_state_volume(s) >= semantic_state_volume(s)
