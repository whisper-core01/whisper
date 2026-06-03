# tests/test_bal_v01.py

from bal_v01 import BAL
from loader_v01 import Loader
from mce_v01 import MCE


SEED = b"whisper-bal-seed"


def make_bal(route_count=3):
    return BAL(Loader(MCE(SEED)), route_count=route_count)


def test_lane_creation_matches_route_count():
    bal = make_bal(route_count=4)

    assert len(bal.lanes) == 4
    assert [lane.lane_id for lane in bal.lanes] == [0, 1, 2, 3]


def test_fragments_distribute_round_robin():
    bal = make_bal(route_count=3)
    fragments = [b"fragment_%d" % i for i in range(10)]

    bal.distribute(fragments)

    assert bal.lane_loads() == [4, 3, 3]


def test_reassembly_recovers_original_order():
    bal = make_bal(route_count=3)
    fragments = [b"fragment_%d" % i for i in range(25)]

    bal.distribute(fragments)

    assert bal.collect_results() == fragments


def test_deterministic_per_seed():
    fragments = [b"fragment_%d" % i for i in range(20)]

    bal_a = make_bal(route_count=3)
    bal_b = make_bal(route_count=3)

    bal_a.distribute(fragments)
    bal_b.distribute(fragments)

    assert bal_a.lane_loads() == bal_b.lane_loads()
    assert bal_a.collect_results() == bal_b.collect_results()


def test_stress_1000_fragments_across_3_lanes():
    bal = make_bal(route_count=3)
    fragments = [b"fragment_%d" % i for i in range(1000)]

    bal.distribute(fragments)

    assert bal.collect_results() == fragments
    assert sum(bal.lane_loads()) == 1000
    assert bal.lane_loads() == [334, 333, 333]
