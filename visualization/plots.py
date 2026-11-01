from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PLOTS = RESULTS / "plots"


def load_results(filename):
    path = RESULTS / filename

    if not path.exists():
        print(f"Skipping missing file: {path}")
        return None

    return pd.read_csv(path)


def save_plot(filename):
    PLOTS.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(PLOTS / filename, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved plot: {PLOTS / filename}")


def comparison_plot(df, x, y1, y2, xlabel, ylabel, title, filename):
    if not all(column in df.columns for column in [x, y1, y2]):
        print(f"Skipping {filename}: required columns are missing.")
        return

    plt.figure(figsize=(9, 5))
    plt.plot(df[x], df[y1], marker="o", label="Conventional")
    plt.plot(df[x], df[y2], marker="s", label="JDR-inspired")

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.legend()

    save_plot(filename)


def main():
    photon_df = load_results("photon_analysis.csv")
    distance_df = load_results("distance_analysis.csv")

    if photon_df is not None:
        comparison_plot(
            photon_df,
            "mean_photons_per_symbol",
            "conventional_ber",
            "jdr_ber",
            "Mean received photons per symbol",
            "Bit Error Rate",
            "BER vs Received Photon Level",
            "ber_vs_photons.png"
        )

        comparison_plot(
            photon_df,
            "mean_photons_per_symbol",
            "conventional_mutual_information",
            "jdr_mutual_information",
            "Mean received photons per symbol",
            "Mutual Information (bits/codeword)",
            "Mutual Information vs Photon Level",
            "mutual_information_vs_photons.png"
        )

        comparison_plot(
            photon_df,
            "mean_photons_per_symbol",
            "conventional_pie",
            "jdr_pie",
            "Mean received photons per symbol",
            "Photon Information Efficiency (bits/photon)",
            "Photon Information Efficiency vs Photon Level",
            "pie_vs_photons.png"
        )

    if distance_df is not None:
        comparison_plot(
            distance_df,
            "distance_m",
            "conventional_ber",
            "jdr_ber",
            "Transmission Distance (m)",
            "Bit Error Rate",
            "BER vs Transmission Distance",
            "ber_vs_distance.png"
        )

        comparison_plot(
            distance_df,
            "distance_m",
            "conventional_mutual_information",
            "jdr_mutual_information",
            "Transmission Distance (m)",
            "Mutual Information (bits/codeword)",
            "Mutual Information vs Distance",
            "mutual_information_vs_distance.png"
        )

        comparison_plot(
            distance_df,
            "distance_m",
            "conventional_pie",
            "jdr_pie",
            "Transmission Distance (m)",
            "Photon Information Efficiency (bits/photon)",
            "Photon Information Efficiency vs Distance",
            "pie_vs_distance.png"
        )

    print("\nPlot generation finished.")


if __name__ == "__main__":
    main()