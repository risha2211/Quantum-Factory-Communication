
import numpy as np


def simulate_conventional_receiver(
    transmitted_signal: np.ndarray,
    mean_photons_per_symbol: float,
    seed: int = 42
) -> dict:
    """
    Simulate coherent BPSK detection using a simplified
    normalized Gaussian shot-noise model.

    transmitted_signal:
        Array containing BPSK symbols (+1 and -1).

    mean_photons_per_symbol:
        Mean received signal photons per symbol.

    Observation:
        y = 2 * sqrt(mu) * s + n

    where n is standard Gaussian noise.
    """

    signal = np.asarray(transmitted_signal, dtype=float)

    if signal.size == 0:
        raise ValueError("Transmitted signal cannot be empty.")

    if not np.all(np.isin(signal, [-1, 1])):
        raise ValueError("Signal must contain only -1 and +1.")

    if mean_photons_per_symbol < 0:
        raise ValueError("Photon count cannot be negative.")

    rng = np.random.default_rng(seed)

    noise = rng.normal(0, 1, size=signal.shape)

    observations = (
        2 * np.sqrt(mean_photons_per_symbol) * signal
        + noise
    )

    detected_signal = np.where(observations >= 0, 1, -1)

    decoded_bits = ((1 - detected_signal) // 2).astype(int)

    return {
        "observations": observations,
        "detected_signal": detected_signal,
        "decoded_bits": decoded_bits,
        "noise": noise
    }


def calculate_ber(
    transmitted_bits: np.ndarray,
    received_bits: np.ndarray
) -> float:
    """
    Calculate bit error rate.
    """

    transmitted_bits = np.asarray(transmitted_bits)
    received_bits = np.asarray(received_bits)

    if transmitted_bits.shape != received_bits.shape:
        raise ValueError("Bit arrays must have the same shape.")

    if transmitted_bits.size == 0:
        raise ValueError("Bit arrays cannot be empty.")

    return float(np.mean(transmitted_bits != received_bits))


if __name__ == "__main__":

    original_bits = np.array([1, 0, 1, 1, 0, 0, 1, 0])

    transmitted_signal = 1 - 2 * original_bits

    result = simulate_conventional_receiver(
        transmitted_signal,
        mean_photons_per_symbol=2,
        seed=42
    )

    print("\n========== CONVENTIONAL RECEIVER ==========")

    print("Transmitted bits:", original_bits)
    print("Received observations:")
    print(np.round(result["observations"], 3))

    print("Detected bits:", result["decoded_bits"])

    print(
        "BER:",
        calculate_ber(original_bits, result["decoded_bits"])
    )
