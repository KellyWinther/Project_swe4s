import numpy as np
import matplotlib as plt
import pandas as pd
from tqdm import tqdm
import os

# This is used to try and speed up overlap calculations
from numpy.lib.stride_tricks import sliding_window_view

from loading_utils import *
from analysis_utils import *


def find_max_overlap_length(
    l1: list,
    l2: list,
    normalize: bool = True,
) -> int:
    """
    Counts the longest contiguous overlap of values
    between two lists. This function will always
    define l1 and l2 such that l1 is shorter than
    l2. If the user provides two lists that do not
    meet that expectation, the function will re-arrange
    them accordingly.

    Parameters:
    -----------
    l1 :: list | np.array
        A list containing integer values.
    l2 :: list | np.array
        A different list containing integer values.
    normalize :: bool
        Whether or not the 'length' should be normalized
        by the maximum possible overlap length.

    Returns:
    --------
    length :: int
        The length of the largest shared sequence between
        the two lists. If no shared sequence is found, the
        default return in 0.
    """

    # If already Numpy arrays, this does nothing
    l1 = np.asarray(l1)
    l2 = np.asarray(l2)

    # Ensure l1 is the shorter array (swap if needed)
    if len(l1) > len(l2):
        l1, l2 = l2, l1
    na = len(l1)

    # Try longest possible length first
    for length in range(na, 0, -1):
        a_windows = sliding_window_view(l1, length)  # windows of shorter array
        b_windows = sliding_window_view(l2, length)  # windows of longer array

        # Compare each window of l1 against each window of l2
        matches = np.all(
            a_windows[:, None, :] == b_windows[None, :, :], axis=2
        )

        if np.any(matches):

            if normalize:
                length /= na

            return length

    return 0


individual = "7742"

# Defines all the file locations used in this pipeline
# NOTE: If you use this for '7744', you will need to remove 'sleepyvole'
spike_time_filename = os.path.join(
    "../data/full_data/",
    individual,
    "/PartnerIntro/spike_times.npy",
)
cluster_filename = os.path.join(
    "../data/full_data/",
    individual,
    "/PartnerIntro/spike_clusters.npy",
)
KSlabel_filename = os.path.join(
    "../data/full_data/",
    individual,
    "/PartnerIntro/cluster_KSLabel.tsv",
)
behavior_filename = os.path.join(
    "../data/full_data/",
    individual,
    "/PartnerIntro/",
    individual,
    "_Partnerintro_sleepyvole_events_with_indices.csv",
)
swr_filename = os.path.join(
    "../data/full_data/",
    individual,
    "/PartnerIntro/",
    individual,
    "_Partnerintro_sleepyvole_SWRs_ca2.csv",
)

# Loads spike data and filters it based on 'KSLabel'
spike_df = load_spike_data(
    time_dir=spike_time_filename,
    cluster_dir=cluster_filename,
    label_dir=KSlabel_filename,
)
spike_df = filter_dataframe(
    spike_df,
    {"KSLabel": ["good"]},
).reset_index(drop=True)

# Loads in behavior / SWR CSV data
behavior_df = pd.read_csv(behavior_filename)
swr_df = pd.read_csv(swr_filename)

# Prepares / reformats the behavior dataframe
behavior_df = filter_dataframe(
    behavior_df,
    filter_dictionary={"EventType": ["social interaction", "cup interaction"]},
)
behavior_df[["indexStart", "indexEnd"]] /= 2500
behavior_df = behavior_df.rename(
    columns={"indexStart": "Start", "indexEnd": "Stop"}
)

# Since filtering may have dropped rows, we need to reset indices
spike_df = spike_df.reset_index(drop=True)
behavior_df = behavior_df.reset_index(drop=True)

# Will locate events that occur within the respective windows
behavior_cluster_df = group_dataframes_by_time(
    window_df=behavior_df,
    event_df=spike_df,
    event_time_column="Time",
    keep_event_columns=["Cluster ID"],
    time_interval_columns=["Start", "Stop"],
    progress=True,
)
swr_cluster_df = group_dataframes_by_time(
    window_df=swr_df,
    event_df=spike_df,
    event_time_column="Time",
    keep_event_columns=["Cluster ID"],
    time_interval_columns=["Start", "Stop"],
    progress=True,
)

N = 30
behavior_cluster_df = behavior_cluster_df.head(N)
swr_cluster_df = swr_cluster_df.head(N)

overlap_matrix = np.zeros((len(swr_cluster_df), len(behavior_cluster_df)))

# THIS IS THE CORE LOGIC FOR FINDING OVERLAPS
for x in tqdm(range(len(behavior_cluster_df))):

    # Using a variable to prevent repeated lookups in the dataframe
    behavior_sequence = behavior_cluster_df.at[x, "Event Cluster IDs"]

    for y in range(len(swr_cluster_df)):

        if (len(behavior_sequence) == 0) or (
            len(swr_cluster_df.at[y, "Event Cluster IDs"]) == 0
        ):
            continue

        # Indexing is flipped due to the way 'overlap matrix' was initialized
        overlap_matrix[y, x] = find_max_overlap_length(
            swr_cluster_df.at[y, "Event Cluster IDs"],
            behavior_sequence,
            normalize=True,
        )

# Plotting
plt.rcParams["figure.figsize"] = (8, 8)
plt.imshow(overlap_matrix, cmap="inferno", aspect="auto", interpolation="none")
plt.xlabel("Behavior DataFrame Index")
plt.ylabel("SWR DataFrame Index")
plt.colorbar()
plt.show()
