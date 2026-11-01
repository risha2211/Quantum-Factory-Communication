
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------------------------------------------------
# PROJECT CONFIGURATION
# ---------------------------------------------------------

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

st.set_page_config(
    page_title="Quantum-Assisted Optical Communication",
    page_icon="⚛️",
    layout="wide"
)


# ---------------------------------------------------------
# DATA LOADING
# ---------------------------------------------------------

@st.cache_data
def load_csv(filename):
    path = RESULTS / filename

    if path.exists():
        return pd.read_csv(path)

    return None


def show_metric(label, value, help_text=None):
    st.metric(label, value, help=help_text)


def display_download(df, filename, label):
    if df is not None:
        st.download_button(
            label=label,
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=filename,
            mime="text/csv"
        )


def comparison_chart(
    df,
    x_column,
    y_columns,
    title,
    x_label,
    y_label
):
    required = [x_column] + y_columns

    if not all(column in df.columns for column in required):
        st.info("Required experiment columns are unavailable.")
        return

    fig = px.line(
        df,
        x=x_column,
        y=y_columns,
        markers=True,
        labels={
            x_column: x_label,
            "value": y_label,
            "variable": "Receiver"
        },
        title=title
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        legend_title="Receiver",
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)


def display_dataset(df, filename):
    if df is None:
        st.warning(f"{filename} is not available. Run the corresponding experiment.")
        return

    st.dataframe(df, use_container_width=True)
    display_download(
        df,
        filename,
        "Download experiment CSV"
    )


# ---------------------------------------------------------
# LOAD EXPERIMENT DATA
# ---------------------------------------------------------

photon_df = load_csv("photon_analysis.csv")
comparison_df = load_csv("receiver_comparison.csv")
distance_df = load_csv("distance_analysis.csv")


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("⚛️ Quantum-Assisted Optical Wireless Communication")

st.subheader(
    "Simulation-Based Study of Joint Detection for "
    "Photon-Starved Optical Communication"
)

st.markdown(
    """
    An academic simulation platform exploring Hadamard-based
    collective optical detection for smart industrial communication
    environments.
    """
)

st.divider()


# ---------------------------------------------------------
# RESEARCH SCOPE NOTICE
# ---------------------------------------------------------

st.warning(
    """
    **Research scope:** This project implements a simplified
    numerical JDR-inspired receiver model. It does not implement
    physical optical hardware, a complete quantum measurement
    apparatus, or a demonstrated quantum communication advantage.
    """
)


# ---------------------------------------------------------
# NAVIGATION
# ---------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "Overview & Methodology",
    "Photon Analysis",
    "Distance Analysis",
    "Receiver Comparison"
])


# =========================================================
# TAB 1: OVERVIEW AND METHODOLOGY
# =========================================================

with tab1:

    st.header("Project Overview")

    st.markdown(
        """
        ### Research Motivation

        Smart industrial networks require reliable communication
        between robotic systems, sensors and central controllers.

        Optical Wireless Communication (OWC) offers a potential
        communication medium for these environments. However,
        photon-starved conditions can make reliable signal detection
        challenging.

        This project investigates a simplified Joint Detection
        Receiver (JDR)-inspired approach using Hadamard transformations
        and photon-counting simulation.
        """
    )

    st.subheader("Project Objectives")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            - Generate Hadamard matrices.
            - Encode binary information using BPSK.
            - Model optical photon transmission.
            - Simulate conventional coherent detection.
            """

        )

    with col2:
        st.markdown(
            """
            - Implement a Hadamard-transform-based receiver.
            - Simulate Poisson photon counting.
            - Evaluate BER and mutual information.
            - Study photon-level and distance effects.
            """
        )

    st.divider()

    # SYSTEM ARCHITECTURE

    st.subheader("System Architecture")

    st.markdown(
        """
        The simulation follows the communication pipeline below:
        """
    )

    stages = [
        ("1. Transmitter", "Binary input and BPSK encoding"),
        ("2. Hadamard Encoder", "Orthogonal codeword generation"),
        ("3. Optical Channel", "Photon budget and channel attenuation"),
        ("4. Receiver", "Conventional or JDR-inspired detection"),
        ("5. Evaluation", "BER, mutual information and PIE"),
        ("6. Visualization", "Plots, CSV results and dashboard")
    ]

    for i, (heading, description) in enumerate(stages):
        st.markdown(
            f"""
            **{heading}**

            {description}
            """
        )

        if i != len(stages) - 1:
            st.markdown("↓")

    st.divider()

    # METHODOLOGY

    st.subheader("Simulation Methodology")

    with st.expander("1. Hadamard Matrix Generation", expanded=False):

        st.markdown(
            """
            Hadamard matrices are generated using the Sylvester
            construction.

            Starting with:

            \\[
            H_1 = [1]
            \\]

            The recursive construction is:

            \\[
            H_{2N} =
            \\begin{bmatrix}
            H_N & H_N \\\\
            H_N & -H_N
            \\end{bmatrix}
            \\]

            The orthogonality property is:

            \\[
            HH^T = NI
            \\]

            This provides a set of mutually orthogonal codewords.
            """
        )

    with st.expander("2. BPSK Encoding", expanded=False):

        st.markdown(
            """
            Binary data is mapped to BPSK symbols:

            \\[
            0 \\rightarrow +1
            \\]

            \\[
            1 \\rightarrow -1
            \\]

            Groups of binary bits select Hadamard codeword indices.
            """

        )

    with st.expander("3. Optical Channel and Photon Budget", expanded=False):

        st.markdown(
            """
            The transmitted photon count per symbol is estimated using:

            \\[
            N_t = \\frac{P_t \\lambda}{R_s h c}
            \\]

            Where:

            - \\(P_t\\): Transmitted optical power
            - \\(\\lambda\\): Optical wavelength
            - \\(R_s\\): Symbol rate
            - \\(h\\): Planck's constant
            - \\(c\\): Speed of light

            The channel model includes geometric collection efficiency,
            atmospheric attenuation and optical efficiency.
            """
        )

    with st.expander("4. Conventional Receiver", expanded=False):

        st.markdown(
            """
            The conventional receiver uses a simplified normalized
            Gaussian BPSK observation model:

            \\[
            y = 2\\sqrt{\\mu}s+n
            \\]

            Here, \\(\\mu\\) is the received signal photon level,
            \\(s\\) is the transmitted BPSK symbol, and \\(n\\)
            represents Gaussian noise.

            The implementation includes an illustrative
            background-dependent noise variance approximation.
            """
        )

    with st.expander("5. JDR-Inspired Receiver", expanded=False):

        st.markdown(
            """
            The receiver applies a normalized Hadamard transformation:

            \\[
            U_H = \\frac{H}{\\sqrt{N}}
            \\]

            For an ideal Hadamard codeword:

            \\[
            U_H H_i^T = \\sqrt{N}e_i
            \\]

            The transformed signal concentrates into one output mode.

            Photon counts are sampled using Poisson distributions.
            The receiver selects the output mode with the highest
            observed photon count, randomizing decisions when
            multiple modes tie.
            """
        )

    st.divider()

    # METRICS

    st.subheader("Performance Metrics")

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    with metric_col1:
        st.markdown("### BER")
        st.markdown("**Bit Error Rate**")
        st.latex(r"BER = \frac{\text{Incorrect bits}}{\text{Total transmitted bits}}")
        st.caption("Measures the fraction of incorrectly decoded bits.")

    with metric_col2:
        st.markdown("### MI")
        st.markdown("**Mutual Information**")
        st.latex(r"I(X;Y)=\sum_{x,y}p(x,y)\log_2\frac{p(x,y)}{p(x)p(y)}")
        st.caption("Measures information shared by transmitted and detected messages.")

    with metric_col3:
        st.markdown("### PIE")
        st.markdown("**Photon Information Efficiency**")
        st.latex(r"PIE=\frac{I(X;Y)}{\text{Mean photons per block}}")
        st.caption("Measures estimated information per received photon.")

    st.divider()

    # MODEL LIMITATIONS

    st.subheader("Assumptions and Limitations")

    st.markdown(
        """
        **1. Idealized collective transformation**

        The JDR-inspired receiver assumes an ideal normalized
        Hadamard transformation. Optical processing loss,
        alignment errors and hardware imperfections are not
        explicitly modelled.

        **2. Different receiver noise models**

        The conventional receiver uses a Gaussian observation
        model with an illustrative background-dependent variance.
        The JDR-inspired receiver uses Poisson photon counting.
        These models are not physically equivalent.

        **3. Simplified optical channel**

        Geometric beam spreading and atmospheric attenuation
        are modelled using simplified assumptions.

        **4. Reference-calibrated distance experiment**

        The distance experiment uses a reference received photon
        level of 0.5 photons per symbol at 100 m. Other distances
        are scaled using relative channel efficiency.

        **5. Simulation rather than hardware validation**

        Results represent numerical simulations and should not
        be interpreted as experimental measurements.

        **6. Mutual information versus channel capacity**

        Mutual information is estimated for the simulated input
        distribution. It is not necessarily the optimized
        channel capacity.
        """
    )

    st.divider()

    st.subheader("Experiment Dataset Availability")

    availability_col1, availability_col2, availability_col3 = st.columns(3)

    with availability_col1:
        st.metric(
            "Photon Analysis",
            "Available" if photon_df is not None else "Missing"
        )

    with availability_col2:
        st.metric(
            "Distance Analysis",
            "Available" if distance_df is not None else "Missing"
        )

    with availability_col3:
        st.metric(
            "Receiver Comparison",
            "Available" if comparison_df is not None else "Missing"
        )


# =========================================================
# TAB 2: PHOTON ANALYSIS
# =========================================================

with tab2:

    st.header("Photon-Level Analysis")

    st.markdown(
        """
        This experiment investigates how changing the mean received
        photon level per symbol affects receiver performance.
        """
    )

    if photon_df is None:

        st.warning("Photon analysis dataset is not available.")

    else:

        st.subheader("Bit Error Rate")

        comparison_chart(
            photon_df,
            "mean_photons_per_symbol",
            ["conventional_ber", "jdr_ber"],
            "Bit Error Rate vs Received Photon Level",
            "Mean Received Photons per Symbol",
            "Bit Error Rate"
        )

        st.subheader("Mutual Information")

        comparison_chart(
            photon_df,
            "mean_photons_per_symbol",
            [
                "conventional_mutual_information",
                "jdr_mutual_information"
            ],
            "Mutual Information vs Photon Level",
            "Mean Received Photons per Symbol",
            "Mutual Information (bits/codeword)"
        )

        st.subheader("Photon Information Efficiency")

        comparison_chart(
            photon_df,
            "mean_photons_per_symbol",
            ["conventional_pie", "jdr_pie"],
            "Photon Information Efficiency vs Photon Level",
            "Mean Received Photons per Symbol",
            "Photon Information Efficiency (bits/photon)"
        )

        st.subheader("Experiment Results")

        display_dataset(
            photon_df,
            "photon_analysis.csv"
        )


# =========================================================
# TAB 3: DISTANCE ANALYSIS
# =========================================================

with tab3:

    st.header("Distance-Based Analysis")

    st.markdown(
        """
        This experiment studies the effect of transmission distance
        on the received photon level and receiver performance.
        """
    )

    st.info(
        """
        **Reference calibration:** 0.5 received photons per symbol
        at 100 m. Other photon levels are calculated using relative
        geometric and atmospheric channel efficiencies.
        """
    )

    if distance_df is None:

        st.warning("Distance experiment dataset is not available.")

    else:

        st.subheader("Bit Error Rate vs Distance")

        comparison_chart(
            distance_df,
            "distance_m",
            ["conventional_ber", "jdr_ber"],
            "Bit Error Rate vs Transmission Distance",
            "Transmission Distance (m)",
            "Bit Error Rate"
        )

        st.subheader("Mutual Information vs Distance")

        comparison_chart(
            distance_df,
            "distance_m",
            [
                "conventional_mutual_information",
                "jdr_mutual_information"
            ],
            "Mutual Information vs Transmission Distance",
            "Transmission Distance (m)",
            "Mutual Information (bits/codeword)"
        )

        st.subheader("Received Photon Level")

        if "mean_photons_per_symbol" in distance_df.columns:

            fig = px.line(
                distance_df,
                x="distance_m",
                y="mean_photons_per_symbol",
                markers=True,
                title="Received Photons per Symbol vs Distance",
                labels={
                    "distance_m": "Transmission Distance (m)",
                    "mean_photons_per_symbol": "Received Photons per Symbol"
                }
            )

            fig.update_layout(template="plotly_white")

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.subheader("Distance Experiment Results")

        display_dataset(
            distance_df,
            "distance_analysis.csv"
        )


# =========================================================
# TAB 4: RECEIVER COMPARISON
# =========================================================

with tab4:

    st.header("Receiver Performance Comparison")

    st.markdown(
        """
        This section compares the simulated output of the conventional
        Gaussian BPSK receiver and the JDR-inspired Poisson
        photon-counting receiver.
        """
    )

    if comparison_df is None:

        st.warning("Receiver comparison dataset is not available.")

    else:

        if not comparison_df.empty:

            first = comparison_df.iloc[0]

            st.caption(
                "Summary for the first operating point in the dataset."
            )

            col1, col2 = st.columns(2)

            with col1:

                if "conventional_ber" in comparison_df.columns:

                    show_metric(
                        "Conventional Receiver BER",
                        f"{first['conventional_ber']:.6f}"
                    )

            with col2:

                if "jdr_ber" in comparison_df.columns:

                    show_metric(
                        "JDR-Inspired Receiver BER",
                        f"{first['jdr_ber']:.6f}"
                    )

            st.divider()

            if all(
                column in comparison_df.columns
                for column in [
                    "conventional_mutual_information",
                    "jdr_mutual_information"
                ]
            ):

                st.subheader("Mutual Information Comparison")

                comparison_chart(
                    comparison_df,
                    "mean_photons_per_symbol",
                    [
                        "conventional_mutual_information",
                        "jdr_mutual_information"
                    ],
                    "Receiver Mutual Information Comparison",
                    "Mean Received Photons per Symbol",
                    "Mutual Information (bits/codeword)"
                )

            if all(
                column in comparison_df.columns
                for column in ["conventional_pie", "jdr_pie"]
            ):

                st.subheader("Photon Information Efficiency Comparison")

                comparison_chart(
                    comparison_df,
                    "mean_photons_per_symbol",
                    ["conventional_pie", "jdr_pie"],
                    "Receiver Photon Information Efficiency",
                    "Mean Received Photons per Symbol",
                    "Bits per Photon"
                )

        st.subheader("Complete Comparison Dataset")

        display_dataset(
            comparison_df,
            "receiver_comparison.csv"
        )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.markdown(
    """
    <div style="text-align:center;">

    **Quantum-Assisted Optical Wireless Communication**

    Simulation-based academic research project

    Numerical results are subject to the assumptions and
    limitations described in the methodology section.

    </div>
    """,
    unsafe_allow_html=True
)
