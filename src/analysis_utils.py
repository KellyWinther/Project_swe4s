import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import os
import sys


def make_correlation_dictionary(
    df: pd.DataFrame,
    id_column_name: str = "Event Cluster IDs",
    normalize: bool = True,
) -> dict:
    """
    Generates a dictionary that indicates how many
    times each neuron cluster fired when any other
    cluster had also fired. The output is a nested
    dictionary where the first key indicates the
    cluster of interest, and the second key indicates
    whether or not another given neuron fired. So,
    for example...

        corr_dict[7][16]

    ...would tell you how many times cluster 16 fired
    out of all times that cluster 7 fired.

    Parameters:
    -----------
    df :: pd.DataFrame
        A dataframe that contains information about
        which neuron clusters fired for each detected
        SWR. This function assumes that the 'ID' column
        has a list for every row of the dataframe.
    id_column_name :: str
        Name of the column that cluster ID is stored in.
    normalize :: bool
        Controls whether recorded counts are normalized.
        If 'True', each second key (i.e., 16) is divided
        by the total number of counts for the first key
        (i.e., 7).

    Returns:
    --------
    corr_dict :: dict
        A nested dictionary showing how many times each
        cluster fired with another neuron cluster.
    """

    # Using 'np.sum()' appends all lists together, and 'flatten()' makes it 1D
    all_ids = np.array(np.sum(df[id_column_name])).flatten()
    unique_ids = np.unique(all_ids)

    # Initialized with 0 in case a cluster never fires with the reference one
    corr_dict = {key: {key: 0 for key in unique_ids} for key in unique_ids}

    for baseline_id in tqdm(unique_ids, desc="Building correlation dict."):
        for compared_id in unique_ids:
            for row in df[id_column_name]:

                # Only true if both clusters fires during the same SWR
                if (baseline_id in row) and (compared_id in row):
                    corr_dict[baseline_id][compared_id] += 1

        if normalize:

            # The original dictionary value is modified, so we have to store it
            baseline_value = corr_dict[baseline_id][baseline_id]
            for compared_id in unique_ids:
                try:
                    corr_dict[baseline_id][compared_id] /= baseline_value
                except ZeroDivisionError:
                    corr_dict[baseline_id][compared_id] = 0

    return corr_dict


def visualize_correlation_dictionary(
    corr_matrix: dict,
    save_directory: str = None,
):
    """
    Plots a 'correlation matrix' plot for a given
    correlation dictionary. The x-axis shows the baseline
    neuron cluster id, and the y-axis shows the compared cluster
    id. The color is controlled by the value found for that
    baseline-referenced pair in the dictionary.

    Parameters:
    -----------
    corr_matrix :: dict
        A nested dictionary containing information about the
        co-firing of two neuron clusters.
    save_directory :: str
        The directory (path + filename) to save the correlation
        matrix image to. If no argument is provided, the image
        will not be saved and 'plt.show()' will be called
        instead.
    """

    # Initializes grid with zeros in case no information is found for an id
    shape = (len(corr_matrix), len(corr_matrix))
    grid = np.zeros(shape)

    keys = list(corr_matrix.keys())

    # Populates matrix with values found in the dictionary
    for i in range(len(grid)):
        for j in range(len(grid)):
            grid[j][i] = corr_matrix[keys[i]][keys[j]]

    # Plots correlation matrix and adds a colorbar
    plt.rcParams["figure.figsize"] = (9, 7)
    plt.imshow(grid, origin="lower", interpolation="none", cmap="inferno")
    plt.colorbar(label="Probability of Co-Activity")

    # Adds labels to plot
    plt.title("Correlation Matrix for Neuron Clusters")
    plt.xlabel("Cluster ID (baseline)")
    plt.ylabel("Cluster ID (compared)")

    # Replacing default xtick labels with cluster ids
    plt.xticks(range(len(keys)), labels=keys, rotation=90, fontsize=7)
    plt.yticks(range(len(keys)), labels=keys, fontsize=7)

    if save_directory:
        plt.savefig(save_directory, bbox_inches="tight")
        plt.close()
        plt.clf()
    else:
        plt.show()


def match_up(
    df: pd.DataFrame,
    swr_dir: str = None,
    swr_df: pd.DataFrame = None,
    only_keep_good: bool = True,
    progress: bool = True,
) -> pd.DataFrame:
    """
    Assigns each SWR its list of spike times and cluster IDs.

    You can pass either:
      - swr_dir: path to SWR CSV
      - swr_df: already-loaded SWR DataFrame (faster for permutations)
    """
    if swr_df is None and swr_dir is None:
        raise ValueError("Provide either swr_dir or swr_df")

    spike_df = df.copy()

    # Load SWR data if path is given
    if swr_df is None:
        try:
            swr_df = pd.read_csv(swr_dir)
        except FileNotFoundError:
            print(f"File not found: {swr_dir}")
            sys.exit(1)
    else:
        swr_df = swr_df.copy()

    if only_keep_good:
        spike_df = spike_df[spike_df["KSLabel"] == "good"]

    swr_df["Spike Times (s)"] = None
    swr_df["Cluster IDs"] = None
    swr_df = swr_df.astype(
        {"Spike Times (s)": "object", "Cluster IDs": "object"}
    )

    spike_times = np.array(spike_df["Time"])
    cluster_ids = np.array(spike_df["Cluster ID"])

    for idx in tqdm(
        range(len(swr_df)), desc="Checking SWR Data", disable=not progress
    ):
        mask = (swr_df["Start"][idx] <= spike_times) & (
            spike_times <= swr_df["Stop"][idx]
        )
        swr_df.at[idx, "Spike Times (s)"] = list(spike_times[mask])
        swr_df.at[idx, "Cluster IDs"] = list(cluster_ids[mask])

    return swr_df


def count_spikes(
    swr_df: pd.DataFrame,
    mode: str = "all",
) -> dict:
    """
    Count spikes per cluster across SWRs.

    Parameters
    ----------
    swr_df : pd.DataFrame
        Must contain columns:
        - "Spike Times (s)" : list/array of spike times
        - "Cluster IDs"     : list/array of cluster IDs
    mode : str
        "all" count all spikes of each cluster within each SWR
        "first" count only the first spike cluster per SWR

    Returns
    -------
    dict : {cluster_id: count}
    """

    if mode not in ("first", "all"):
        raise ValueError("mode must be 'first' or 'all'")

    counts = {}

    for _, row in swr_df.iterrows():
        times = row["Spike Times (s)"]
        clusters = row["Cluster IDs"]

        # Skip empty SWRs
        if times is None or len(times) == 0:
            continue

        times = np.array(times, dtype=float)
        clusters = np.array(clusters, dtype=float)

        if mode == "first":
            # find first spike
            first_cluster = clusters[np.argmin(times)]
            counts[first_cluster] = counts.get(first_cluster, 0) + 1

        elif mode == "all":
            # count every spike event
            unique, freqs = np.unique(clusters, return_counts=True)
            for cid, f in zip(unique, freqs):
                counts[cid] = counts.get(cid, 0) + f

    return counts


def compute_mean_firing_rates(
    spike_df: pd.DataFrame,
    total_duration: float = None
):
    """Compute mean firing rate (Hz) for each cluster."""
    if total_duration is None:
        total_duration = spike_df["Time"].max()
    counts = spike_df["Cluster ID"].value_counts()
    firing_rates = counts / total_duration  # spikes per second

    return firing_rates.to_dict()


def compute_true_counts(
    swr_df: pd.DataFrame,
    spike_df: pd.DataFrame,
    total_duration: float,
    mode: str,
) -> tuple[dict, dict]:
    """
    Compute firing rates and observed spike counts during SWRs.

    Parameters
    ----------
    swr_df : pd.DataFrame
        DataFrame containing SWR windows and their associated spike times.
    spike_df : pd.DataFrame
        Full spike train dataset containing at least 'Time' and 'ClusterID'.
    total_duration : float
        Total recording duration in seconds.
    mode : {"first", "all"}
        Spike counting mode:
        - "first": count only the first spike per SWR.
        - "all": count all spikes occurring in each SWR.

    Returns
    -------
    firing_rates : dict
        Mapping of cluster_id -> firing rate (Hz).
    true_counts : dict
        Mapping of cluster_id -> observed spike count in true SWRs.
    """
    firing_rates = compute_mean_firing_rates(spike_df, total_duration)
    true_counts = count_spikes(swr_df, mode=mode)
    return firing_rates, true_counts


def generate_shifts(
    n_permutations: int,
    shift_range_seconds: float,
) -> np.ndarray:
    """
    Generate random circular shift values for permutation testing.

    Parameters
    ----------
    n_permutations : int
        Number of permutations to generate.
    shift_range_seconds : float
        Range of uniform shifts. Values will be sampled from:
        [-shift_range_seconds, +shift_range_seconds].

    Returns
    -------
    np.ndarray
        Array of random shift values of shape (n_permutations,).
    """
    return np.random.uniform(
        -shift_range_seconds, shift_range_seconds, size=n_permutations
    )


def apply_circular_shift(
    swr_df: pd.DataFrame,
    shift: float,
    total_duration: float,
):
    """
    Apply a circular temporal shift to SWR start/stop timestamps.

    Parameters
    ----------
    swr_df : pd.DataFrame
        Original SWR dataframe with 'Start' and 'Stop' columns.
    shift : float
        Amount of time (seconds) to shift SWR windows.
    total_duration : float
        Total duration of the recording. Used for modulo wrap-around.

    Returns
    -------
    pd.DataFrame
        New SWR dataframe with shifted (wrapped) start and stop times.
    """
    shifted = swr_df.copy()
    shifted["Start"] = (shifted["Start"] + shift) % total_duration
    shifted["Stop"] = (shifted["Stop"] + shift) % total_duration
    return shifted


def compute_permutation_counts(
    shifts: list | np.ndarray,
    swr_df: pd.DataFrame,
    spike_df: pd.DataFrame,
    total_duration: float,
    mode: str,
    progress: bool = True,
):
    """
    Generate spike-count dictionaries for each permutation.

    Parameters
    ----------
    shifts : array-like
        List/array of shift values to apply for each permutation.
    swr_df : pd.DataFrame
        Original SWR dataframe.
    spike_df : pd.DataFrame
        Full spike dataset, used for matching spikes to shifted SWRs.
    total_duration : float
        Recording duration for circular wrap-around.
    mode : {"first", "all"}
        Spike counting mode for SWR windows.
    progress : bool, default True
        Whether to show tqdm progress bar.

    Yields
    ------
    dict
        Mapping cluster_id -> spike counts for that permutation.
    """
    for shift in tqdm(shifts, disable=not progress):
        shifted = apply_circular_shift(swr_df, shift, total_duration)
        shifted = match_up(
            df=spike_df, swr_df=shifted, only_keep_good=False, progress=False
        )
        yield count_spikes(shifted, mode=mode)


def aggregate_permuted_counts(
    true_counts: dict,
    perm_generator: dict,
) -> dict:
    """
    Collect permutation spike counts across all permutations.

    Parameters
    ----------
    true_counts : dict
        Observed true spike counts per cluster. Needed to initialize keys.
    perm_generator : iterable of dict
        Yields dictionaries of permutation spike counts.

    Returns
    -------
    dict
        Mapping cluster_id -> list of spike counts across permutations.
    """
    out = {cid: [] for cid in true_counts.keys()}

    for perm_counts in perm_generator:
        for cid in out.keys():
            out[cid].append(perm_counts.get(cid, 0))

    return out


def compute_stats_for_cluster(
    cid: int | float,
    true_val: int,
    perm_vals: list | np.ndarray,
    rate: float,
    tail: str = "two",
):
    """
    Compute statistical metrics for one neuron.

    Parameters
    ----------
    cid : int or float
        Cluster ID.
    true_val : int
        Observed spike count in the true SWR dataset.
    perm_vals : array-like
        Null distribution of spike counts for this neuron.
    rate : float
        Neuron firing rate in Hz.
    tail : {"one", "two"}
        Type of p-value test:
        - "one" one-sided is greater
        - "two" two-sided is greater or less (default)

    Returns
    -------
    dict
        Dictionary containing statistical metrics including:
        z-score, p-value, normalized counts, etc.
    """
    perm_vals = np.array(perm_vals)
    mean_perm = perm_vals.mean()
    std_perm = perm_vals.std(ddof=1) + 1e-6

    # --- p-value ---
    if tail == "one":
        p_value = (np.sum(perm_vals >= true_val) + 1) / (len(perm_vals) + 1)
    else:
        p_value = (
            np.sum(
                np.abs(perm_vals - mean_perm) >= np.abs(true_val - mean_perm)
            )
            + 1
        ) / (len(perm_vals) + 1)

    # --- normalized counts ---
    normalized_true = true_val / rate if rate > 0 else np.nan
    normalized_mean = mean_perm / rate if rate > 0 else np.nan

    # --- z-score ---
    z_score = (true_val - mean_perm) / std_perm

    return {
        "Cluster ID": cid,
        "Firing Rate (Hz)": rate,
        "True Count": true_val,
        "Mean Permuted": mean_perm,
        "Normalized True": normalized_true,
        "Normalized Mean": normalized_mean,
        "Z-Score": z_score,
        f"p-value ({tail}-tailed)": p_value,
    }


def build_results_table(
    true_counts: dict,
    all_permuted_counts: dict,
    firing_rates: dict,
    tail: str = "two",
):
    """
    Build a results DataFrame from permutation outcomes.

    Parameters
    ----------
    true_counts : dict
        Observed spike counts per cluster.
    all_permuted_counts : dict
        Permutation null distribution for each cluster.
    firing_rates : dict
        Firing rates per cluster in Hz.
    tail : {"one", "two"}
        Tailedness of p-value calculation.

    Returns
    -------
    pd.DataFrame
        Table of permutation statistics for all neurons.
    """
    rows = []
    for cid, true_val in true_counts.items():
        perm_vals = all_permuted_counts[cid]
        rate = firing_rates.get(cid, np.nan)
        rows.append(
            compute_stats_for_cluster(cid, true_val, perm_vals, rate, tail)
        )
    return pd.DataFrame(rows)


def save_results(
    result_df: pd.DataFrame,
    save_path: str,
):
    """
    Save results as a CSV file if a save path is provided.

    Parameters
    ----------
    result_df : pd.DataFrame
        DataFrame of permutation metrics.
    save_path : str or None
        Path to save the CSV file. If None, no file is saved.
    """
    if save_path is None:
        return

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    result_df.to_csv(save_path, index=False)


# Full wrapper function to create circular permutation test
# and histograms for individual neuron spike data in SWRs
def circular_permutation_test_with_firing_rate(
    swr_df: pd.DataFrame,
    spike_df: pd.DataFrame,
    tail: str = "two",
    total_duration: float = None,
    n_permutations: int = 1000,
    shift_range_seconds: float = 3.0,
    progress: bool = True,
    save_path: str = None,
    mode: str = "all",
) -> tuple[pd.DataFrame, dict, dict]:
    """
    Run a full circular-permutation test on SWR spike data.

    This wrapper function coordinates the modular components:
    - firing rate computation
    - true spike counts
    - shift generation
    - permutation counting
    - null distribution aggregation
    - statistical testing
    - optional saving

    Parameters
    ----------
    swr_df : pd.DataFrame
        SWR dataframe with spike timings per event.
    spike_df : pd.DataFrame
        Full spike dataset (Time, ClusterID).
    tail : {"one", "two"}, default "two"
        Tailedness of p-value test.
    total_duration : float, optional
        Recording duration in seconds. If None, uses max spike time.
    n_permutations : int, default 1000
        Number of circular permutations.
    shift_range_seconds : float, default 3.0
        Uniform shift range (±shift_range_seconds).
    progress : bool, default True
        Whether to show tqdm progress bar.
    save_path : str or None
        Output path for saving results CSV.
    mode : {"first", "all"}, default "all"
        Spike counting strategy for SWRs.
        first: count only first spike per SWR.
        all: count all spikes in each SWR.

    Returns
    -------
    result_df : pd.DataFrame
        Final results table per cluster.
    true_counts : dict
        Observed spike counts per cluster.
    all_permuted_counts : dict
        Permutation null distributions per cluster.
    """
    if total_duration is None:
        total_duration = spike_df["Time"].max()

    firing_rates, true_counts = compute_true_counts(
        swr_df, spike_df, total_duration, mode
    )

    shifts = generate_shifts(n_permutations, shift_range_seconds)

    perm_gen = compute_permutation_counts(
        shifts, swr_df, spike_df, total_duration, mode, progress
    )

    all_permuted_counts = aggregate_permuted_counts(true_counts, perm_gen)

    result_df = build_results_table(
        true_counts, all_permuted_counts, firing_rates, tail
    )

    save_results(result_df, save_path)

    return result_df, true_counts, all_permuted_counts
