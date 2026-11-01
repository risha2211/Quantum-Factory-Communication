
import numpy as np

from src.hadamard import (
    generate_hadamard,
    generate_bpsk_codebook,
    bpsk_modulate
)


def text_to_bits(message: str) -> list[int]:
    """
    Convert a text message into a binary bit sequence
    using UTF-8 encoding.
    """

    binary = ''.join(
        format(byte, '08b')
        for byte in message.encode('utf-8')
    )

    return [int(bit) for bit in binary]


def bits_to_text(bits: list[int]) -> str:
    """
    Convert a binary bit sequence back into text.
    The input must contain complete 8-bit bytes.
    """

    if len(bits) % 8 != 0:
        raise ValueError("Bit sequence must contain complete bytes.")

    binary = ''.join(str(bit) for bit in bits)

    byte_values = [
        int(binary[i:i + 8], 2)
        for i in range(0, len(binary), 8)
    ]

    return bytes(byte_values).decode('utf-8')


def encode_bits_to_hadamard(
    bits: list[int],
    block_size: int = 8
) -> dict:
    """
    Encode groups of log2(N) message bits into
    Hadamard-based BPSK codewords.

    Returns the transmitted signal and encoding metadata.
    """

    if block_size < 2 or block_size & (block_size - 1):
        raise ValueError("Block size must be a power of 2 >= 2.")

    if not bits:
        raise ValueError("Message cannot be empty.")

    if any(bit not in (0, 1) for bit in bits):
        raise ValueError("Input must contain only binary bits.")

    bits_per_codeword = int(np.log2(block_size))

    H = generate_hadamard(block_size)
    codebook = generate_bpsk_codebook(H)

    padding = (
        bits_per_codeword - len(bits) % bits_per_codeword
    ) % bits_per_codeword

    padded_bits = bits + [0] * padding

    message_indices = []

    for i in range(0, len(padded_bits), bits_per_codeword):

        group = padded_bits[i:i + bits_per_codeword]

        index = int(''.join(map(str, group)), 2)

        message_indices.append(index)

    selected_codewords = codebook[message_indices]

    transmitted_signal = bpsk_modulate(selected_codewords)

    return {
        "original_bits": bits,
        "padded_bits": padded_bits,
        "padding_bits": padding,
        "message_indices": message_indices,
        "binary_codewords": selected_codewords,
        "transmitted_signal": transmitted_signal,
        "block_size": block_size,
        "bits_per_codeword": bits_per_codeword
    }


if __name__ == "__main__":

    message = "101101"

    bits = [int(bit) for bit in message]

    result = encode_bits_to_hadamard(bits, block_size=8)

    print("\n========== TRANSMITTER SIMULATION ==========")

    print("Original message:", message)
    print("Message bits:", result["original_bits"])

    print("Block size:", result["block_size"])
    print("Bits per codeword:", result["bits_per_codeword"])

    print("Message indices:", result["message_indices"])

    print("\nSelected binary codewords:")
    print(result["binary_codewords"])

    print("\nBPSK transmitted signal:")
    print(result["transmitted_signal"])

    print("\nPadding bits:", result["padding_bits"])

    print("\nTransmitter simulation completed.")
