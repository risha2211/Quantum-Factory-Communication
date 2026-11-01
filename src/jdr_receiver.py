
import numpy as np

from src.hadamard import (
    generate_hadamard,
    normalize_hadamard
)


def transform_codeword(codeword: np.ndarray) -> np.ndarray:
    """
    Apply a normalized Hadamard transformation to a BPSK
    codeword.

    For a Hadamard row x_i:

        U_H @ x_i = sqrt(N) * e_i
    """

    codeword = np.asarray(codeword, dtype=float)

    if codeword.ndim != 1:
        raise ValueError("Codeword must be one-dimensional.")

    n = len(codeword)

    if n < 2 or n & (n - 1):
        raise ValueError("Codeword length must be a power of 2 >= 2.")

    if not np.all(np.isin(codeword, [-1, 1])):
        raise ValueError("Codeword must contain only -1 and +1.")

    H = generate_hadamard(n)
    U = normalize_hadamard(H)

    return U @ codeword


def simulate_jdr_receiver(
    transmitted_signal: np.ndarray,
    mean_photons_per_symbol: float,
    background_photons_per_mode: float = 0.0,
    seed: int = 42
) -> dict:
    """
    Simulate an idealized Hadamard-transform-based
    collective photon-counting receiver.

    Each input row is a BPSK Hadamard codeword.

    The normalized Hadamard transformation concentrates
    the ideal signal into one output mode.

    Photon counts are sampled independently from Poisson
    distributions.

    When multiple modes have the same maximum count,
    one of those modes is selected uniformly at random.

    This is a numerical model, not a physical optical
    receiver implementation.
    """

    signal = np.asarray(transmitted_signal, dtype=float)

    if signal.ndim != 2:
        raise ValueError("Input must be a 2D codeword array.")

    if signal.shape[0] == 0:
        raise ValueError("At least one codeword is required.")

    n = signal.shape[1]

    if n < 2 or n & (n - 1):
        raise ValueError("Codeword length must be a power of 2 >= 2.")

    if not np.all(np.isin(signal, [-1, 1])):
        raise ValueError("Signal must contain only -1 and +1.")

    if mean_photons_per_symbol < 0:
        raise ValueError("Photon count cannot be negative.")

    if background_photons_per_mode < 0:
        raise ValueError("Background photon count cannot be negative.")

    H = generate_hadamard(n)
    U = normalize_hadamard(H)

    rng = np.random.default_rng(seed)

    transformed_modes = []
    photon_counts = []
    detected_indices = []
    detected_codewords = []

    for codeword in signal:

        optical_amplitudes = (
            np.sqrt(mean_photons_per_symbol) * codeword
        )

        output_amplitudes = U @ optical_amplitudes

        signal_photons = np.abs(output_amplitudes) ** 2

        mean_output_counts = (
            signal_photons + background_photons_per_mode
        )

        counts = rng.poisson(mean_output_counts)

        # Randomize ties instead of always choosing mode zero.
        maximum_count = np.max(counts)

        tied_modes = np.flatnonzero(counts == maximum_count)

        detected_index = int(rng.choice(tied_modes))

        detected_indices.append(detected_index)
        detected_codewords.append(H[detected_index])
        transformed_modes.append(output_amplitudes)
        photon_counts.append(counts)

    return {
        "transformed_modes": np.asarray(transformed_modes),
        "photon_counts": np.asarray(photon_counts),
        "detected_indices": np.asarray(detected_indices),
        "detected_codewords": np.asarray(detected_codewords)
    }


def decode_hadamard_indices(
    indices: np.ndarray,
    block_size: int
) -> np.ndarray:
    """Convert detected Hadamard indices into binary message blocks."""

    if block_size < 2 or block_size & (block_size - 1):
        raise ValueError("Block size must be a power of 2 >= 2.")

    indices = np.asarray(indices, dtype=int)

    if np.any(indices < 0) or np.any(indices >= block_size):
        raise ValueError("Invalid Hadamard codeword index.")

    bits_per_codeword = int(np.log2(block_size))

    decoded_bits = []

    for index in indices:
        binary = format(index, f"0{bits_per_codeword}b")
        decoded_bits.extend(int(bit) for bit in binary)

    return np.asarray(decoded_bits, dtype=int)


if __name__ == "__main__":

    H = generate_hadamard(8)

    transmitted_signal = np.vstack([
        H[3],
        H[5]
    ])

    result = simulate_jdr_receiver(
        transmitted_signal,
        mean_photons_per_symbol=2,
        background_photons_per_mode=0.01,
        seed=42
    )

    decoded_bits = decode_hadamard_indices(
        result["detected_indices"],
        block_size=8
    )

    print("\n========== JDR-INSPIRED RECEIVER ==========")
    print("Transmitted codeword indices: [3, 5]")

    print("\nTransformed optical modes:")
    print(np.round(result["transformed_modes"], 3))

    print("\nPhoton counts:")
    print(result["photon_counts"])

    print("\nDetected indices:")
    print(result["detected_indices"])

    print("\nDecoded message bits:")
    print(decoded_bits)
