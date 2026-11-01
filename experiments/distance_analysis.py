from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation import evaluate_receivers


# Illustrative optical channel parameters
WAVELENGTH_M = 1550e-9
DIVERGENCE_RAD = 1e-3
APERTURE_RADIUS_M = 0.05
ATTENUATION_DB_PER_KM = 0.1

REFERENCE_DISTANCE_M = 100
REFERENCE_RECEIVED_PHOTONS = 0.5


def geometric_efficiency(distance_m):
    """Uniform circular beam approximation."""
    beam_radius = distance_m * np.tan(DIVERGENCE_RAD)

    if beam_radius <= 0:
        raise ValueError("Distance must be positive.")

    return min(1.0, (APERTURE_RADIUS_M / beam_radius) ** 2)


def atmospheric_efficiency(distance_m):
    """Atmospheric transmission using dB/km attenuation."""
    distance_km = distance_m / 1000
    return 10 ** (
        -ATTENUATION_DB_PER_KM * distance_km / 10
    )


def relative_received_photons(distance_m):
    """
    Reference-calibrated photon model.

    The received photon level is calibrated to 0.5 photons/symbol
    at 100 m. Other distances are scaled using relative geometric
    and atmospheric transmission.
    """
    reference_factor = (
        geometric_efficiency(REFERENCE_DISTANCE_M)
        * atmospheric_efficiency(REFERENCE_DISTANCE_M)
    )

    current_factor = (
        geometric_efficiency(distance_m)
        * atmospheric_efficiency(distance_m)
    )

    return REFERENCE_RECEIVED_PHOTONS * (
        current_factor / reference_factor
    )


def main():
    distances = [10, 25, 50, 75, 100, 125, 150, 200]
    rows = []

    print("\nDISTANCE-BASED COMMUNICATION EXPERIMENT")
    print("=" * 65)
    print("Reference calibration: 0.5 photons/symbol at 100 m")

    for distance in distances:
        photons = relative_received_photons(distance)

        print(
            f"\nDistance: {distance} m | "
            f"Received photons/symbol: {photons:.8f}"
        )

        result = evaluate_receivers(
            block_size=8,
            mean_photons_per_symbol=photons,
            background_photons_per_mode=0,
            trials_per_codeword=1000,
            seed=42
        )

        row = {
            "distance_m": distance,
            "mean_photons_per_symbol": photons,
            "geometric_efficiency": geometric_efficiency(distance),
            "atmospheric_efficiency": atmospheric_efficiency(distance),
        }

        for key, value in result.items():
            if isinstance(value, (int, float, np.number)):
                row[key] = float(value)
            elif isinstance(value, dict):
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, (int, float, np.number)):
                        row[f"{key}_{subkey}"] = float(subvalue)

        rows.append(row)

        print(f"Conventional BER: {result['conventional_ber']:.6f}")
        print(f"JDR-inspired BER: {result['jdr_ber']:.6f}")

    output_dir = ROOT / "results"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "distance_analysis.csv"
    df = pd.DataFrame(rows)
    df.to_csv(output_file, index=False)

    print("\n" + "=" * 65)
    print("DISTANCE EXPERIMENT COMPLETED")
    print(df.to_string(index=False))
    print(f"\nSaved to: {output_file}")


if __name__ == "__main__":
    main()