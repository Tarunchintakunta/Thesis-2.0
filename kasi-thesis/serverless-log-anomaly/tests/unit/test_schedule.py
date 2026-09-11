import random
from collections import Counter

import pytest

from logad.inject.faults import CATEGORIES, LIVE_COMMANDS, check_category
from logad.inject.schedule import active_at, build_schedule, read_ground_truth, write_ground_truth


def make(per_category=60, block_size=12, seed=0):
    return build_schedule(0.0, per_category, block_size, (360, 720), (120, 240), random.Random(seed))


def test_240_injections_balanced_over_categories():
    sched = make()
    assert len(sched) == 240
    assert Counter(i.category for i in sched) == {c: 60 for c in CATEGORIES}


def test_every_block_has_three_of_each():
    sched = make()
    for block in range(20):
        cats = Counter(i.category for i in sched if i.block == block)
        assert cats == {c: 3 for c in CATEGORIES}


def test_intervals_do_not_overlap_and_respect_bounds():
    sched = make()
    prev_end = 0.0
    for inj in sched:
        assert inj.start - prev_end >= 360 - 1e-9
        assert 120 <= inj.end - inj.start <= 240
        prev_end = inj.end


def test_active_at():
    sched = make(per_category=3, block_size=4)
    inj = sched[5]
    assert active_at(sched, (inj.start + inj.end) / 2) == inj
    assert active_at(sched, inj.start - 1) is None
    assert active_at(sched, inj.end) is None


def test_ground_truth_roundtrip(tmp_path):
    sched = make(per_category=3, block_size=4)
    path = write_ground_truth(sched, tmp_path / "gt.csv")
    assert read_ground_truth(path) == sched


def test_bad_block_sizes_are_rejected():
    with pytest.raises(ValueError):
        make(block_size=10)
    with pytest.raises(ValueError):
        make(per_category=5, block_size=12)


def test_categories_have_live_commands():
    assert set(LIVE_COMMANDS) == set(CATEGORIES)
    assert all({"on", "off"} <= set(v) for v in LIVE_COMMANDS.values())
    with pytest.raises(ValueError):
        check_category("cosmic_rays")
