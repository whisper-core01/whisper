# tests/test_voxmesh_v01.py

from voxmesh_v01 import VoxMesh


SEED = b"whisper-voxmesh-seed"


def test_36_fractals_created():
    mesh = VoxMesh(SEED)

    assert len(mesh.fractals) == 36
    assert mesh.coherence_check() is True


def test_mutation_changes_state():
    mesh = VoxMesh(SEED)
    before = mesh.get_states_hex()

    mesh.mutate_all(b"entropy")

    after = mesh.get_states_hex()

    assert before != after
    assert mesh.coherence_check() is True


def test_divergence_increases_or_remains_maximal_over_time():
    mesh = VoxMesh(SEED)

    initial = mesh.get_divergence_score()

    for i in range(10):
        mesh.mutate_all(b"entropy_%d" % i)

    final = mesh.get_divergence_score()

    assert 0.0 <= initial <= 1.0
    assert 0.0 <= final <= 1.0
    assert final >= initial


def test_coherence_check_detects_bad_state():
    mesh = VoxMesh(SEED)
    mesh.fractals[0].state = b"bad"

    assert mesh.coherence_check() is False


def test_determinism_per_seed():
    mesh_a = VoxMesh(SEED)
    mesh_b = VoxMesh(SEED)

    for i in range(10):
        entropy = b"entropy_%d" % i
        mesh_a.mutate_all(entropy)
        mesh_b.mutate_all(entropy)

    assert mesh_a.get_states_hex() == mesh_b.get_states_hex()
    assert mesh_a.get_divergence_score() == mesh_b.get_divergence_score()
