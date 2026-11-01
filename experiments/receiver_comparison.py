
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation import evaluate_receivers


def main():
    print("\nCONVENTIONAL vs JDR-INSPIRED RECEIVER")
    print("=" * 55)

    photon_levels = [0.1, 0.5, 1.0]
    rows = []

    for photons in photon_levels:
        print(f"\nTesting {photons} photons per symbol...")

        result = evaluate_receivers(
            block_size=8,
            mean_photons_per_symbol=photons,
            background_photons_per_mode=0,
            trials_per_codeword=2000,
            seed=42
        )

        row = {"mean_photons_per_symbol": photons}

        for key, value in result.items():
            if isinstance(value, (int, float)):
                row[key] = value
            elif isinstance(value, dict):
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, (int, float)):
                        row[f"{key}_{subkey}"] = subvalue

        rows.append(row)

    output_dir = ROOT / "results"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "receiver_comparison.csv"
    pd.DataFrame(rows).to_csv(output_file, index=False)

    print("\nComparison results:")
    print(pd.DataFrame(rows).to_string(index=False))
    print(f"\nSaved to: {output_file}")


if __name__ == "__main__":
    main()