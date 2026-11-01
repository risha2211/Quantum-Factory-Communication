
import numpy as np


def estimate_transition_matrix(
    transmitted_indices: np.ndarray,
    detected_indices: np.ndarray,
    number_of_codewords: int
) -> np.ndarray:
    """
    Estimate P(Y=j | X=i) from transmitted and detected
    codeword indices.

    Each row represents a transmitted codeword.
    Each column represents a detected codeword.
    """

    transmitted = np.asarray(transmitted_indices, dtype=int)
    detected = np.asarray(detected_indices, dtype=int)

    if transmitted.shape != detected.shape or transmitted.size == 0:
        raise ValueError("Input arrays must have equal, nonzero length.")

    if number_of_codewords <= 1:
        raise ValueError("At least two codewords are required.")

    if (
        np.any(transmitted < 0)
        or np.any(transmitted >= number_of_codewords)
        or np.any(detected < 0)
        or np.any(detected >= number_of_codewords)
    ):
        raise ValueError("Codeword indices are out of range.")

    matrix = np.zeros(
        (number_of_codewords, number_of_codewords),
        dtype=float
    )

    for x, y in zip(transmitted, detected):
        matrix[x, y] += 1

    row_totals = matrix.sum(axis=1)

    if np.any(row_totals == 0):
        raise ValueError("Every input codeword must have observations.")

    matrix /= row_totals[:, None]

    return matrix


def calculate_mutual_information(
    transition_matrix: np.ndarray,
    input_probabilities: np.ndarray = None
) -> float:
    """
    Calculate mutual information I(X;Y), in bits per
    codeword, from a conditional transition matrix.

    Assumes a uniform input distribution if none is supplied.
    """

    conditional = np.asarray(transition_matrix, dtype=float)

    if conditional.ndim != 2 or conditional.shape[0] != conditional.shape[1]:
        raise ValueError("Transition matrix must be square.")

    if np.any(conditional < 0):
        raise ValueError("Probabilities cannot be negative.")

    if not np.allclose(conditional.sum(axis=1), 1):
        raise ValueError("Every transition matrix row must sum to 1.")

    n = conditional.shape[0]

    if input_probabilities is None:
        px = np.full(n, 1 / n)
    else:
        px = np.asarray(input_probabilities, dtype=float)

        if px.shape != (n,) or np.any(px < 0):
            raise ValueError("Invalid input probability distribution.")

        if not np.isclose(px.sum(), 1):
            raise ValueError("Input probabilities must sum to 1.")

    joint = px[:, None] * conditional
    py = joint.sum(axis=0)

    mutual_information = 0.0

    for i in range(n):
        for j in range(n):
            if joint[i, j] > 0 and py[j] > 0:
                mutual_information += joint[i, j] * np.log2(
                    joint[i, j] / (px[i] * py[j])
                )

    return float(mutual_information)


def calculate_photon_information_efficiency(
    mutual_information_bits: float,
    mean_received_photons: float
) -> float:
    """
    Calculate photon information efficiency in bits per photon.

    The information and photon count must refer to the same
    unit of communication, e.g. one complete codeword block.
    """

    if mutual_information_bits < 0:
        raise ValueError("Mutual information cannot be negative.")

    if mean_received_photons <= 0:
        raise ValueError("Mean received photons must be positive.")

    return mutual_information_bits / mean_received_photons


def calculate_channel_capacity(
    transition_matrix: np.ndarray,
    input_probabilities: np.ndarray = None
) -> float:
    """
    Calculate mutual information for a specified input
    distribution.

    With a uniform input, this is the mutual information
    under uniform codeword transmission, not necessarily
    the maximum channel capacity.
    """

    return calculate_mutual_information(
        transition_matrix,
        input_probabilities
    )


if __name__ == "__main__":

    transition = np.array([
        [0.90, 0.05, 0.05],
        [0.05, 0.90, 0.05],
        [0.05, 0.05, 0.90]
    ])

    information = calculate_mutual_information(transition)

    pie = calculate_photon_information_efficiency(
        information,
        mean_received_photons=3.0
    )

    print("\n========== INFORMATION ANALYSIS ==========")
    print("Transition probability matrix:")
    print(transition)

    print(f"\nMutual information: {information:.4f} bits/block")
    print(f"Photon information efficiency: {pie:.4f} bits/photon")
