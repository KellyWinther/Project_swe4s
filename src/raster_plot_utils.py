import pandas as pd
import matplotlib.pyplot as plt


def prep_raster(df):
    """
    Prepare long-form spike–ripple aligned data for raster plotting.
    Works directly on the output of match_times(), which includes:
        - 'Peak'
        - 'Event Times'
        - 'Event Cluster IDs'

    Adds:
        - ripple_idx  (for selecting ripples later)
    """

    if df is None:
        raise ValueError("No DataFrame provided.")

    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected a pandas DataFrame, got {type(df)}.")

    required = ["Peak", "Event Times", "Event Cluster IDs"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Input dataframe is missing columns: {missing}")

    # --- Add ripple index before exploding ---
    df = df.copy()
    df["ripple_idx"] = df.index

    # --- Rename match_times output to standard names ---
    df = df.rename(columns={
        "Event Times": "Spike Times (s)",
        "Event Cluster IDs": "Cluster IDs"
    })

    # --- Convert stringified lists if needed ---
    for col in ["Spike Times (s)", "Cluster IDs"]:
        if isinstance(df[col].iloc[0], str):
            from ast import literal_eval
            df[col] = df[col].apply(literal_eval)

    # --- Expand each spike entry ---
    exp_df = df.explode(["Spike Times (s)", "Cluster IDs"], ignore_index=True)
    exp_df = exp_df.dropna(subset=["Spike Times (s)", "Cluster IDs"])

    # --- Compute time relative to peak ---
    exp_df["t_rel"] = exp_df["Spike Times (s)"] - exp_df["Peak"]

    print(f"prep_raster: {len(exp_df)} spikes from {df.shape[0]} ripple(s)")

    return exp_df

def select_ripples_to_plot(exp_df, ripple_index=None):
    """
    Select spikes belonging to specific ripple indices from the exploded dataframe.

    Parameters
    ----------
    exp_df : pandas.DataFrame
        The exploded dataframe produced by prep_raster().
    ripple_index : None, int, or list-like
        None = return all ripples
        int = return that ripple
        list = return multiple ripples
    """

    if ripple_index is None:
        return exp_df.copy()

    # Normalize input type
    if isinstance(ripple_index, int):
        ripple_index = [ripple_index]

    if not hasattr(ripple_index, "__iter__"):
        raise TypeError("ripple_index must be None, an int, or an iterable of ints.")

    ripple_index = list(ripple_index)

    if any(not isinstance(i, int) for i in ripple_index):
        raise ValueError("All ripple indices must be integers.")

    # --- NEW CHECK: ensure indices exist in the dataset ---
    valid_indices = set(exp_df["ripple_idx"].unique())
    invalid = [i for i in ripple_index if i not in valid_indices]

    if invalid:
        raise ValueError(
            f"Invalid ripple index/indices {invalid}. "
            f"Valid ripple indices are between {min(valid_indices)} and {max(valid_indices)}."
        )

    # Now safe to subset
    sub = exp_df[exp_df["ripple_idx"].isin(ripple_index)].copy()

    return sub


def plot_raster(
        exp_df,
        height=9,
        width=6,
        color="black",
        tick_width=1,
        window=0.1,
    ):
    """
    Plot a raster with evenly spaced cluster rows, labeled by actual cluster IDs.
    """

    if "t_rel" not in exp_df.columns:
        raise ValueError("Expected 't_rel' column. Run prep_raster() first.")

    # Filter by window
    mask = (exp_df["t_rel"] >= -window) & (exp_df["t_rel"] <= window)
    raster_df = exp_df.loc[mask].copy()

    # Sort clusters for consistent vertical ordering
    clusters = sorted(raster_df["Cluster IDs"].unique())
    
    # Map each cluster ID to a row index (0..N-1)
    cluster_to_row = {cid: i for i, cid in enumerate(clusters)}
    raster_df["cluster_row"] = raster_df["Cluster IDs"].map(cluster_to_row)

    # Plot
    fig, ax = plt.subplots(figsize=(height, width))
    ax.scatter(
        raster_df["t_rel"],
        raster_df["cluster_row"],
        s=tick_width,
        color=color,
        alpha=0.7,
    )

    # Vertical line at ripple peak (t_rel = 0)
    ax.axvline(0, color="red", linestyle="--", linewidth=2)

    # Formatting
    ax.set_xlim(-window, window)
    ax.set_xlabel("Time (s) relative to ripple peak")
    ax.set_ylabel("Cluster ID")
    ax.set_title(f"Spiking Activity at Ripple Peak (±{window*1000:.0f} ms)")

    # Set evenly spaced y-ticks but with real cluster labels
    ax.set_yticks(range(len(clusters)))
    ax.set_yticklabels(clusters)

    plt.tight_layout()
    plt.show()
