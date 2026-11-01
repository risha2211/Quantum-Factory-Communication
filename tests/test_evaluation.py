
import numpy as np
import pytest

from src.capacity import (
    estimate_transition_matrix,
    calculate_mutual_information,
    calculate_photon_information_efficiency
)

from src.evaluation import (
    decode_conventional_codewords,
    evaluate_receivers
)

from src.hadamard import generate_hadamard


def test_transition_matrix_rows_sum_to_one():
    transmitted = np.array([0, 0, 1, 1, 2, 2])
    detected = np.array([0, 0, 1, 2, 2, 2])

    matrix = estimate_transition_matrix(
        transmitted, detected, 3
    )

    assert np.allclose(matrix.sum(axis=1), 1)


def test_perfect_transition_matrix_mutual_information():
    matrix = np.eye(4)

    information = calculate_mutual_information(matrix)

    assert information == pytest.approx(2.0)


def test_zero_information_channel():
    matrix = np.full((4, 4), 0.25)

    information = calculate_mutual_information(matrix)

    assert information == pytest.approx(0.0)


def test_mutual_information_bounds():
    matrix = np.eye(8)

    information = calculate_mutual_information(matrix)

    assert 0 <= information <= 3


def test_photon_information_efficiency():
    pie = calculate_photon_information_efficiency(4, 2)

    assert pie == pytest.approx(2)


def test_conventional_codeword_decoding():
    H = generate_hadamard(8)

    detected = np.vstack([H[2], H[5]])

    indices = decode_conventional_codewords(detected, H)

    assert np.array_equal(indices, [2, 5])


def test_receiver_evaluation_output():
    result = evaluate_receivers(
        block_size=8,
        mean_photons_per_symbol=2,
        background_photons_per_mode=0,
        trials_per_codeword=100,
        seed=42
    )

    assert 0 <= result["conventional_ber"] <= 1
    assert 0 <= result["jdr_ber"] <= 1

    assert 0 <= result["conventional_mutual_information"] <= 3
    assert 0 <= result["jdr_mutual_information"] <= 3

    assert np.allclose(
        result["jdr_transition"].sum(axis=1),
        1
    )


def test_receiver_evaluation_reproducible():
    first = evaluate_receivers(
        trials_per_codeword=50,
        seed=42
    )

    second = evaluate_receivers(
        trials_per_codeword=50,
        seed=42
    )

    assert first["jdr_ber"] == second["jdr_ber"]
    assert first["conventional_ber"] == second["conventional_ber"]


def test_invalid_transition_probabilities():
    matrix = np.array([
        [0.5, 0.5],
        [0.3, 0.3]
    ])

    with pytest.raises(ValueError):
        calculate_mutual_information(matrix)
