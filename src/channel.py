
import numpy as np

# Physical constants
PLANCK_CONSTANT = 6.62607015e-34
SPEED_OF_LIGHT = 299792458


def calculate_transmitted_photons(
    power_w: float,
    wavelength_m: float,
    symbol_rate: float
) -> float:
    """
    Calculate the mean number of transmitted photons per symbol.

    N = P * wavelength / (symbol_rate * h * c)
    """

    if power_w <= 0:
        raise ValueError("Transmitted power must be positive.")

    if wavelength_m <= 0 or symbol_rate <= 0:
        raise ValueError("Wavelength and symbol rate must be positive.")

    return (
        power_w * wavelength_m
        / (symbol_rate * PLANCK_CONSTANT * SPEED_OF_LIGHT)
    )


def calculate_geometric_efficiency(
    distance_m: float,
    divergence_mrad: float,
    receiver_aperture_m: float
) -> float:
    """
    Estimate the fraction of a uniformly distributed,
    circular beam collected by the receiver aperture.

    This is a simplified geometric beam-spreading model.
    """

    if distance_m < 0:
        raise ValueError("Distance cannot be negative.")

    if divergence_mrad <= 0:
        raise ValueError("Beam divergence must be positive.")

    if receiver_aperture_m <= 0:
        raise ValueError("Receiver aperture must be positive.")

    divergence_rad = divergence_mrad * 1e-3

    receiver_radius = receiver_aperture_m / 2

    beam_radius = max(
        distance_m * np.tan(divergence_rad),
        receiver_radius
    )

    efficiency = (receiver_radius / beam_radius) ** 2

    return float(np.clip(efficiency, 0, 1))


def calculate_atmospheric_efficiency(
    distance_m: float,
    attenuation_db_per_km: float
) -> float:
    """
    Calculate atmospheric transmission efficiency
    from attenuation expressed in dB/km.
    """

    if distance_m < 0 or attenuation_db_per_km < 0:
        raise ValueError("Distance and attenuation cannot be negative.")

    distance_km = distance_m / 1000

    loss_db = attenuation_db_per_km * distance_km

    return 10 ** (-loss_db / 10)


def calculate_channel_efficiency(
    distance_m: float,
    divergence_mrad: float,
    receiver_aperture_m: float,
    attenuation_db_per_km: float = 0.1,
    optical_efficiency: float = 0.7
) -> dict:
    """
    Combine geometric, atmospheric and optical losses.
    """

    if not 0 < optical_efficiency <= 1:
        raise ValueError("Optical efficiency must be in (0, 1].")

    geometric = calculate_geometric_efficiency(
        distance_m,
        divergence_mrad,
        receiver_aperture_m
    )

    atmospheric = calculate_atmospheric_efficiency(
        distance_m,
        attenuation_db_per_km
    )

    total = geometric * atmospheric * optical_efficiency

    return {
        "geometric_efficiency": geometric,
        "atmospheric_efficiency": atmospheric,
        "optical_efficiency": optical_efficiency,
        "total_efficiency": total
    }


def calculate_photon_budget(
    power_w: float,
    wavelength_m: float,
    symbol_rate: float,
    channel_efficiency: float,
    background_photons: float = 0.0
) -> dict:
    """
    Calculate transmitted and received mean photon counts.
    """

    if not 0 <= channel_efficiency <= 1:
        raise ValueError("Channel efficiency must be between 0 and 1.")

    if background_photons < 0:
        raise ValueError("Background photons cannot be negative.")

    transmitted = calculate_transmitted_photons(
        power_w,
        wavelength_m,
        symbol_rate
    )

    signal_received = transmitted * channel_efficiency

    total_received = signal_received + background_photons

    return {
        "transmitted_photons": transmitted,
        "signal_received_photons": signal_received,
        "background_photons": background_photons,
        "received_photons": total_received
    }


def sample_photon_counts(
    mean_photons: float,
    number_of_symbols: int,
    seed: int = 42
) -> np.ndarray:
    """
    Generate Poisson-distributed photon counts.

    This models photon arrival statistics, not BPSK
    phase discrimination.
    """

    if mean_photons < 0:
        raise ValueError("Mean photon count cannot be negative.")

    if number_of_symbols <= 0:
        raise ValueError("Number of symbols must be positive.")

    rng = np.random.default_rng(seed)

    return rng.poisson(
        mean_photons,
        size=number_of_symbols
    )


if __name__ == "__main__":

    # Factory optical communication example
    power = 1e-3
    wavelength = 1550e-9
    symbol_rate = 4e9

    print("\n========== OPTICAL CHANNEL SIMULATION ==========")

    # Photon budget for the paper's approximate
    # transmitted/received photon scenario.
    transmitted = calculate_transmitted_photons(
        power,
        wavelength,
        symbol_rate
    )

    target_efficiency = 0.5 / transmitted

    print(f"\nTransmitted power: {power * 1000:.3f} mW")
    print(f"Wavelength: {wavelength * 1e9:.0f} nm")
    print(f"Symbol rate: {symbol_rate / 1e9:.1f} GBd")

    print(f"\nTransmitted photons/symbol: {transmitted:.2f}")
    print(f"Efficiency for 0.5 received photons: {target_efficiency:.3e}")

    reference_budget = calculate_photon_budget(
        power,
        wavelength,
        symbol_rate,
        target_efficiency
    )

    print(
        "Reference received photons/symbol:",
        reference_budget["received_photons"]
    )

    # Illustrative geometric channel
    channel = calculate_channel_efficiency(
        distance_m=10,
        divergence_mrad=1,
        receiver_aperture_m=0.1
    )

    print("\n========== GEOMETRIC CHANNEL ==========")

    for key, value in channel.items():
        print(f"{key}: {value:.6e}")

    budget = calculate_photon_budget(
        power,
        wavelength,
        symbol_rate,
        channel["total_efficiency"],
        background_photons=0.01
    )

    print("\n========== RECEIVED PHOTON BUDGET ==========")

    for key, value in budget.items():
        print(f"{key}: {value:.4f}")

    counts = sample_photon_counts(
        budget["received_photons"],
        number_of_symbols=10
    )

    print("\nSample photon counts:", counts)

    print("\nOptical channel simulation completed.")
