
from src.transmitter import (
    text_to_bits,
    bits_to_text,
    encode_bits_to_hadamard
)


def test_text_conversion():
    message = "Robot"
    bits = text_to_bits(message)

    assert bits_to_text(bits) == message


def test_message_encoding():
    bits = [1, 0, 1, 1, 0, 1]

    result = encode_bits_to_hadamard(bits, 8)

    assert result["message_indices"] == [5, 5]
    assert result["transmitted_signal"].shape == (2, 8)


def test_bpsk_values():
    bits = [1, 0, 1]

    result = encode_bits_to_hadamard(bits, 8)

    signal = result["transmitted_signal"]

    assert set(signal.flatten()).issubset({-1, 1})


def test_padding():
    bits = [1, 0, 1, 1]

    result = encode_bits_to_hadamard(bits, 8)

    assert result["padding_bits"] == 2
    assert len(result["padded_bits"]) == 6
