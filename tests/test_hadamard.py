
import numpy as np

from src.hadamard import (
    generate_hadamard,
    normalize_hadamard,
    verify_orthogonality,
    generate_bpsk_codebook
)


def test_hadamard_dimensions():
    H = generate_hadamard(8)
    assert H.shape == (8, 8)


def test_hadamard_entries():
    H = generate_hadamard(8)
    assert set(np.unique(H)) == {-1, 1}


def test_orthogonality():
    H = generate_hadamard(8)
    assert verify_orthogonality(H)


def test_normalized_transform():
    H = generate_hadamard(8)
    U = normalize_hadamard(H)

    assert np.allclose(U @ U.T, np.eye(8))


def test_codebook():
    H = generate_hadamard(8)
    codebook = generate_bpsk_codebook(H)

    assert codebook.shape == (8, 8)
    assert set(np.unique(codebook)) == {0, 1}
