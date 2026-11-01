
from pathlib import Path
import sys

import pandas as pd

# Allow running this file directly from the project root.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation import evaluate_receivers


def flatten_metrics(result):
    """Keep scalar metrics and ignore arrays such as raw photon counts."""
    metrics = {}

    for key, value in result.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                if isinstance(subvalue, (int, float)):
                    metrics[f"{key}_{subkey}"] = subvalue
        elif isinstance(value, (int, float)):
            metrics[key] = value

    return metrics


def main():
    photon_levels = [0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
    rows = []

    print("\nPHOTON-LEVEL EXPERIMENT")
    print("=" * 55)

    for photons in photon_levels:
        print(f"\nRunning at {photons} received photons per symbol...")

        result = evaluate_receivers(
            block_size=8,
            mean_photons_per_symbol=photons,
            background_photons_per_mode=0,
            trials_per_codeword=1000,
            seed=42
        )

        row = {
            "mean_photons_per_symbol": photons,
            **flatten_metrics(result)
        }
        rows.append(row)

        print("Returned metrics:")
        for key, value in row.items():
            if key != "mean_photons_per_symbol":
                print(f"  {key}: {value}")

    output_dir = ROOT / "results"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "photon_analysis.csv"
    pd.DataFrame(rows).to_csv(output_file, index=False)

    print("\n" + "=" * 55)
    print(f"Experiment complete. Results saved to:\n{output_file}")


if __name__ == "__main__":
    main()
