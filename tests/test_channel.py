
import numpy as np
import pytest

from src.channel import (
    calculate_transmitted_photons,
    calculate_geometric_efficiency,
    calculate_atmospheric_efficiency,
    calculate_channel_efficiency,
    calculate_photon_budget,
    sample_photon_counts
)


def test_transmitted_photons():
    photons = calculate_transmitted_photons(
        1e-3, 1550e-9, 4e9
    )

    assert photons == pytest.approx(1.95e6, rel=0.01)


def test_geometric_efficiency_range():
    efficiency = calculate_geometric_efficiency(
        10, 1, 0.1
    )

    assert 0 <= efficiency <= 1


def test_geometric_efficiency_decreases_with_distance():
    near = calculate_geometric_efficiency(100, 1, 0.1)
    far = calculate_geometric_efficiency(200, 1, 0.1)

    assert far < near


def test_atmospheric_efficiency():
    efficiency = calculate_atmospheric_efficiency(1000, 1)

    assert efficiency == pytest.approx(10 ** (-0.1))


def test_channel_efficiency():
    result = calculate_channel_efficiency(
        10, 1, 0.1
    )

    assert 0 < result["total_efficiency"] <= 1


def test_photon_budget():
    result = calculate_photon_budget(
        1e-3, 1550e-9, 4e9, 1e-6
    )

    assert result["transmitted_photons"] > 0
    assert result["received_photons"] > 0


def test_photon_sampling():
    counts = sample_photon_counts(5, 100)

    assert len(counts) == 100
    assert np.all(counts >= 0)


def test_invalid_channel_efficiency():
    with pytest.raises(ValueError):
        calculate_photon_budget(
            1e-3, 1550e-9, 4e9, 1.5
        )
