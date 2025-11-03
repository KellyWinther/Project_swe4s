import pandas as pd
import matplotlib.pyplot as plt
import sys
import ast

# the following functions help make raster plots


def mega_raster(
    df: pd.DataFrame,
    window: float = 0.1,
):
    """
    Generate a merged raster plot of cluster spiking aligned to ripple peaks.

    Parameters
    ----------
    df :: pandas.DataFrame
        DataFrame with at least these columns:
        - "Peak"
        - "Spike Times (s)"
        - "Cluster IDs"
    window :: float, optional
        Time window (in seconds) to show around ripple peak (default ±0.1 s).
    """
    # confirm data loads with required columns
    try:
        # --- Check if df exists ---
        if df is None:
            raise ValueError("No DataFrame provided.")

        # --- Check if df is actually a pandas DataFrame ---
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Needed a pandas DataFrame, got a {type(df)}.")

        # --- Check for required columns ---
        required_cols = ["Peak", "Spike Times (s)", "Cluster IDs"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: '{col}'")

    except (ValueError, TypeError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    # --- Convert stringified lists to real lists (if needed) ---
    for col in ["Spike Times (s)", "Cluster IDs"]:
        if isinstance(df[col].iloc[0], str):
            df[col] = df[col].apply(ast.literal_eval)

    # --- Expand each ripple into a long-form dataframe ---
    expanded_rows = []
    for _, row in df.iterrows():
        peak = float(row["Peak"])
        spike_times = [float(s) for s in row["Spike Times (s)"]]
        clusters = row["Cluster IDs"]

        for spk_time, clust in zip(spike_times, clusters):
            expanded_rows.append(
                {
                    "ripple_peak": peak,
                    "spike_time": spk_time,
                    "cluster_id": clust,
                    "t_rel": spk_time - peak,  # time relative to ripple peak
                }
            )

    expanded_df = pd.DataFrame(expanded_rows)

    # --- Filter to ±window seconds around each ripple ---
    mask = (expanded_df["t_rel"] >= -window) & (expanded_df["t_rel"] <= window)
    plot_df = expanded_df.loc[mask]

    print(f"Plotting {len(plot_df)} spikes across {len(df)} ripples")

    # --- Raster plot ---
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(plot_df["t_rel"], plot_df["cluster_id"], s=3, color="black", alpha=0.7)
    ax.axvline(0, color="red", linestyle="--", linewidth=1)

    # --- Formatting ---
    ax.set_xlim(-window, window)
    ax.set_xlabel("Time (s) relative to ripple peak")
    ax.set_ylabel("Cluster ID")
    ax.set_title(f"Raster aligned to ripple peaks (±{window*1000:.0f} ms)")

    plt.tight_layout()
    plt.show()


def single_raster(
    df: pd.DataFrame,
    ripple_index: int,
    window: float,
):
    """
    Plot one ripple's cluster spiking activity aligned to its ripple peak.

    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with at least these columns:
        - "Peak"
        - "Spike Times (s)"
        - "Cluster IDs"
    ripple_index :: int, optional
        Row index of the ripple to plot (default = 0, the first ripple)
    window :: float, optional
        Time window around the ripple peak (default ±0.05s)
    """
    # confirm data loads with required columns
    try:
        # --- Check if df exists ---
        if df is None:
            raise ValueError("No DataFrame provided.")

        # --- Check if df is actually a pandas DataFrame ---
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Needed a pandas DataFrame, got a {type(df)}.")

        # --- Check for required columns ---
        required_cols = ["Peak", "Spike Times (s)", "Cluster IDs"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: '{col}'")

    except (ValueError, TypeError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    # === Choose which ripple to plot (0 = first row) ===
    ripple_index = 130  # change this number to view a different ripple
    ripple = df.iloc[ripple_index]

    # Extract relevant info
    peak_time = ripple["Peak"]
    spike_times = ripple["Spike Times (s)"]
    cluster_ids = ripple["Cluster IDs"]

    # Check matching lengths
    assert len(spike_times) == len(
        cluster_ids
    ), "Spike Times and Cluster IDs length mismatch!"

    # Compute time relative to ripple peak
    t_rel = [t - peak_time for t in spike_times]

    # === Define plotting window (±50 ms) ===
    window = 0.05
    x_min, x_max = -window, window

    # === Scale y-axis spacing ===
    scale_y = 2.0  # vertical space between clusters
    unique_clusters = sorted(set(cluster_ids))

    # Map each cluster ID to a scaled position
    cluster_to_scaled = {cid: i * scale_y for i, cid in enumerate(unique_clusters)}
    scaled_y = [cluster_to_scaled[c] for c in cluster_ids]

    # === Raster plot for this ripple ===
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(t_rel, scaled_y, s=50, color="black", marker="|")

    # Add reference line
    ax.axvline(0, color="red", linestyle="--", linewidth=1)

    # Update y-axis ticks to show cluster IDs
    ax.set_yticks([cluster_to_scaled[c] for c in unique_clusters])
    ax.set_yticklabels([str(int(c)) for c in unique_clusters])

    # Axis formatting
    ax.set_xlim(x_min, x_max)
    ax.set_xlabel("Time (s) relative to ripple peak")
    ax.set_ylabel("Active Cluster IDs")
    ax.set_title(
        f"Ripple #{ripple_index} \
                 | Peak = {peak_time:.3f}s | \
                 {len(spike_times)} spikes"
    )

    plt.tight_layout()
    plt.show()
