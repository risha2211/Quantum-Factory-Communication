
import numpy as np
import pytest

from src.hadamard import generate_hadamard
from src.conventional_receiver import (
    simulate_conventional_receiver,
    calculate_ber
)
from src.jdr_receiver import (
    transform_codeword,
    simulate_jdr_receiver,
    decode_hadamard_indices
)


def test_conventional_receiver_output_shape():
    bits = np.array([1, 0, 1, 0])
    signal = 1 - 2 * bits

    result = simulate_conventional_receiver(
        signal, 2, seed=42
    )

    assert result["decoded_bits"].shape == bits.shape


def test_conventional_receiver_valid_bits():
    signal = np.array([1, -1, 1, -1])

    result = simulate_conventional_receiver(
        signal, 2, seed=42
    )

    assert set(np.unique(result["decoded_bits"])).issubset({0, 1})


def test_ber_calculation():
    original = np.array([1, 0, 1, 0])
    received = np.array([1, 0, 0, 0])

    assert calculate_ber(original, received) == 0.25


def test_ber_perfect_detection():
    bits = np.array([1, 0, 1, 0])

    assert calculate_ber(bits, bits) == 0.0


def test_hadamard_transform_concentration():
    H = generate_hadamard(8)

    for i in range(8):
        transformed = transform_codeword(H[i])

        expected = np.zeros(8)
        expected[i] = np.sqrt(8)

        assert np.allclose(transformed, expected)


def test_jdr_receiver_detects_clean_codewords():
    H = generate_hadamard(8)

    transmitted = np.vstack([
        H[1],
        H[3],
        H[5],
        H[7]
    ])

    result = simulate_jdr_receiver(
        transmitted,
        mean_photons_per_symbol=100,
        background_photons_per_mode=0,
        seed=42
    )

    assert np.array_equal(
        result["detected_indices"],
        np.array([1, 3, 5, 7])
    )


def test_jdr_photon_count_shape():
    H = generate_hadamard(8)

    result = simulate_jdr_receiver(
        H[:3],
        mean_photons_per_symbol=5,
        seed=42
    )

    assert result["photon_counts"].shape == (3, 8)


def test_jdr_counts_are_nonnegative():
    H = generate_hadamard(8)

    result = simulate_jdr_receiver(
        H[:3],
        mean_photons_per_symbol=2,
        seed=42
    )

    assert np.all(result["photon_counts"] >= 0)


def test_decode_hadamard_indices():
    indices = np.array([1, 5, 7])

    bits = decode_hadamard_indices(indices, 8)

    assert np.array_equal(
        bits,
        np.array([
            0, 0, 1,
            1, 0, 1,
            1, 1, 1
        ])
    )


def test_invalid_jdr_codeword():
    invalid_signal = np.array([[0, 1, 0, 1]])

    with pytest.raises(ValueError):
        simulate_jdr_receiver(invalid_signal, 2)


def test_negative_photon_count():
    signal = np.array([[1, -1, 1, -1]])

    with pytest.raises(ValueError):
        simulate_jdr_receiver(signal, -1)


def test_negative_background():
    signal = np.array([[1, -1, 1, -1]])

    with pytest.raises(ValueError):
        simulate_jdr_receiver(
            signal, 2, background_photons_per_mode=-1
        )
