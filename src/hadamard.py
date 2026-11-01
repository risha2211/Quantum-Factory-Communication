
import numpy as np


def generate_hadamard(n: int) -> np.ndarray:
    """
    Generate an N x N Hadamard matrix using
    the Sylvester construction.

    N must be a positive power of 2.
    """

    if n < 1 or (n & (n - 1)) != 0:
        raise ValueError("N must be a positive power of 2.")

    H = np.array([[1]], dtype=int)

    while H.shape[0] < n:
        H = np.block([
            [H,  H],
            [H, -H]
        ])

    return H


def normalize_hadamard(H: np.ndarray) -> np.ndarray:
    """
    Convert the Hadamard matrix into a
    normalized orthogonal transform.
    """

    n = H.shape[0]
    return H / np.sqrt(n)


def verify_orthogonality(H: np.ndarray) -> bool:
    """
    Verify the Hadamard orthogonality property:
    H @ H.T = N * I
    """

    n = H.shape[0]
    result = H @ H.T

    return np.array_equal(
        result,
        n * np.eye(n, dtype=int)
    )


def generate_bpsk_codebook(H: np.ndarray) -> np.ndarray:
    """
    Convert Hadamard rows into binary BPSK codewords.

    +1 maps to bit 0
    -1 maps to bit 1
    """

    return ((1 - H) // 2).astype(int)


def bpsk_modulate(bits: np.ndarray) -> np.ndarray:
    """
    BPSK mapping:
    0 -> +1
    1 -> -1
    """

    return 1 - 2 * np.asarray(bits)


if __name__ == "__main__":

    N = 8

    H = generate_hadamard(N)
    U = normalize_hadamard(H)
    codebook = generate_bpsk_codebook(H)

    print("\n========== HADAMARD MATRIX ==========")
    print(H)

    print("\n========== NORMALIZED TRANSFORM ==========")
    print(np.round(U, 3))

    print("\n========== BPSK CODEBOOK ==========")
    print(codebook)

    print("\n========== ORTHOGONALITY TEST ==========")
    print("H x H.T = N x I:", verify_orthogonality(H))

    print("\n========== UNITARY TEST ==========")
    print(
        "U x U.T = I:",
        np.allclose(U @ U.T, np.eye(N))
    )

    print("\nHadamard implementation completed.")
