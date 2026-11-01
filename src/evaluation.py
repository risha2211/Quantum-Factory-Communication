
import numpy as np

from src.hadamard import generate_hadamard
from src.conventional_receiver import simulate_conventional_receiver
from src.jdr_receiver import simulate_jdr_receiver, decode_hadamard_indices
from src.capacity import (
    estimate_transition_matrix,
    calculate_mutual_information,
    calculate_photon_information_efficiency
)


def decode_conventional_codewords(
    detected_symbols: np.ndarray,
    hadamard_matrix: np.ndarray
) -> np.ndarray:
    """
    Decode detected BPSK symbols by choosing the nearest
    Hadamard codeword using Euclidean distance.
    """

    detected = np.asarray(detected_symbols, dtype=float)

    if detected.ndim != 2:
        raise ValueError("Detected symbols must be a 2D array.")

    if detected.shape[1] != hadamard_matrix.shape[1]:
        raise ValueError("Detected codeword length is incorrect.")

    distances = np.sum(
        (detected[:, None, :] - hadamard_matrix[None, :, :]) ** 2,
        axis=2
    )

    return np.argmin(distances, axis=1)


def evaluate_receivers(
    block_size: int = 8,
    mean_photons_per_symbol: float = 0.5,
    background_photons_per_mode: float = 0.0,
    trials_per_codeword: int = 1000,
    seed: int = 42
) -> dict:
    """
    Compare conventional coherent BPSK detection with a
    simplified Hadamard-based collective photon-counting model.

    Both receivers receive the same uniformly distributed
    Hadamard codeword messages.

    Returns measured error rates, transition matrices,
    mutual information and photon information efficiency.
    """

    if block_size < 2 or block_size & (block_size - 1):
        raise ValueError("Block size must be a power of 2 >= 2.")

    if mean_photons_per_symbol < 0:
        raise ValueError("Mean photon count cannot be negative.")

    if background_photons_per_mode < 0:
        raise ValueError("Background photon count cannot be negative.")

    if trials_per_codeword <= 0:
        raise ValueError("Trials per codeword must be positive.")

    n = block_size
    number_of_messages = n

    H = generate_hadamard(n)

    rng = np.random.default_rng(seed)

    # Generate balanced, uniformly distributed codeword messages.
    transmitted_indices = np.repeat(
        np.arange(number_of_messages),
        trials_per_codeword
    )

    rng.shuffle(transmitted_indices)

    transmitted_codewords = H[transmitted_indices]

    # -------------------------------------------------
    # CONVENTIONAL COHERENT BPSK RECEIVER
    # -------------------------------------------------

    conventional_result = simulate_conventional_receiver(
        transmitted_codewords.flatten(),
        mean_photons_per_symbol,
        seed=seed + 1
    )

    detected_symbols = conventional_result["detected_signal"].reshape(
        -1, n
    )

    conventional_indices = decode_conventional_codewords(
        detected_symbols,
        H
    )

    # -------------------------------------------------
    # JDR-INSPIRED COLLECTIVE RECEIVER
    # -------------------------------------------------

    jdr_result = simulate_jdr_receiver(
        transmitted_codewords,
        mean_photons_per_symbol,
        background_photons_per_mode,
        seed=seed + 2
    )

    jdr_indices = jdr_result["detected_indices"]

    # -------------------------------------------------
    # TRANSITION PROBABILITY MATRICES
    # -------------------------------------------------

    conventional_transition = estimate_transition_matrix(
        transmitted_indices,
        conventional_indices,
        number_of_messages
    )

    jdr_transition = estimate_transition_matrix(
        transmitted_indices,
        jdr_indices,
        number_of_messages
    )

    # -------------------------------------------------
    # MESSAGE ERROR RATES
    # -------------------------------------------------

    bits_per_message = int(np.log2(n))

    transmitted_bits = np.array([
        [
            int(bit)
            for bit in format(index, f"0{bits_per_message}b")
        ]
        for index in transmitted_indices
    ])

    conventional_bits = np.array([
        [
            int(bit)
            for bit in format(index, f"0{bits_per_message}b")
        ]
        for index in conventional_indices
    ])

    jdr_bits = np.array([
        [
            int(bit)
            for bit in format(index, f"0{bits_per_message}b")
        ]
        for index in jdr_indices
    ])

    conventional_ber = float(
        np.mean(transmitted_bits != conventional_bits)
    )

    jdr_ber = float(
        np.mean(transmitted_bits != jdr_bits)
    )

    conventional_cwer = float(
        np.mean(transmitted_indices != conventional_indices)
    )

    jdr_cwer = float(
        np.mean(transmitted_indices != jdr_indices)
    )

    # -------------------------------------------------
    # INFORMATION METRICS
    # -------------------------------------------------

    conventional_mi = calculate_mutual_information(
        conventional_transition
    )

    jdr_mi = calculate_mutual_information(
        jdr_transition
    )

    # Each codeword consists of N optical modes.
    mean_photons_per_block = n * (
        mean_photons_per_symbol + background_photons_per_mode
    )

    conventional_pie = (
        calculate_photon_information_efficiency(
            conventional_mi,
            mean_photons_per_block
        )
        if mean_photons_per_block > 0 else 0.0
    )

    jdr_pie = (
        calculate_photon_information_efficiency(
            jdr_mi,
            mean_photons_per_block
        )
        if mean_photons_per_block > 0 else 0.0
    )

    return {
        "parameters": {
            "block_size": n,
            "mean_photons_per_symbol": mean_photons_per_symbol,
            "background_photons_per_mode": background_photons_per_mode,
            "trials_per_codeword": trials_per_codeword,
            "mean_photons_per_block": mean_photons_per_block
        },
        "transmitted_indices": transmitted_indices,
        "conventional_indices": conventional_indices,
        "jdr_indices": jdr_indices,
        "conventional_transition": conventional_transition,
        "jdr_transition": jdr_transition,
        "conventional_ber": conventional_ber,
        "jdr_ber": jdr_ber,
        "conventional_codeword_error_rate": conventional_cwer,
        "jdr_codeword_error_rate": jdr_cwer,
        "conventional_mutual_information": conventional_mi,
        "jdr_mutual_information": jdr_mi,
        "conventional_pie": conventional_pie,
        "jdr_pie": jdr_pie,
        "jdr_photon_counts": jdr_result["photon_counts"]
    }


if __name__ == "__main__":

    result = evaluate_receivers(
        block_size=8,
        mean_photons_per_symbol=0.5,
        background_photons_per_mode=0.01,
        trials_per_codeword=1000
    )

    print("\n========== RECEIVER PERFORMANCE ==========")

    print("\nSimulation parameters:")
    for key, value in result["parameters"].items():
        print(f"{key}: {value}")

    print("\n========== CONVENTIONAL RECEIVER ==========")
    print(f"BER: {result['conventional_ber']:.6f}")
    print(
        "Codeword error rate:",
        f"{result['conventional_codeword_error_rate']:.6f}"
    )
    print(
        "Mutual information:",
        f"{result['conventional_mutual_information']:.4f} bits/block"
    )
    print(
        "PIE:",
        f"{result['conventional_pie']:.4f} bits/photon"
    )

    print("\n========== JDR-INSPIRED RECEIVER ==========")
    print(f"BER: {result['jdr_ber']:.6f}")
    print(
        "Codeword error rate:",
        f"{result['jdr_codeword_error_rate']:.6f}"
    )
    print(
        "Mutual information:",
        f"{result['jdr_mutual_information']:.4f} bits/block"
    )
    print(
        "PIE:",
        f"{result['jdr_pie']:.4f} bits/photon"
    )

    print("\nJDR transition probability matrix:")
    print(np.round(result["jdr_transition"], 3))
