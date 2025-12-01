import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm
import os

from loading_utils import *
from analysis_utils import *
from sequence_matching_utils import *

individual = "7742"

# Defines all the file locations used in this pipeline
# NOTE: If you use this for '7744', you will need to remove 'sleepyvole'
spike_time_filename = os.path.join(
    "../data/full_data",
    individual,
    "PartnerIntro/spike_times.npy",
)

cluster_filename = os.path.join(
    "../data/full_data",
    individual,
    "PartnerIntro/spike_clusters.npy",
)

KSlabel_filename = os.path.join(
    "../data/full_data",
    individual,
    "PartnerIntro/cluster_KSLabel.tsv",
)
behavior_filename = os.path.join(
    "../data/full_data",
    individual,
    "PartnerIntro",
    f"{individual}_Partnerintro_sleepyvole_events_with_indices.csv",
)
swr_filename = os.path.join(
    "../data/full_data",
    individual,
    "PartnerIntro",
    f"{individual}_Partnerintro_sleepyvole_SWRs_ca2.csv",
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

behavior_lists = behavior_cluster_df["Event Cluster IDs"].tolist()
swr_lists = swr_cluster_df["Event Cluster IDs"].tolist()

overlap_matrix = np.zeros((len(swr_cluster_df), len(behavior_cluster_df)))

for x, bseq in enumerate(tqdm(behavior_lists)):
    if not bseq:
        continue

    bset = set(bseq)

    for y, sseq in enumerate(swr_lists):
        if not sseq:
            continue

        # quick elimination based on shared tokens
        if bset.isdisjoint(sseq):
            continue

        overlap_matrix[y, x], seq = lccs_rabin_karp(
            sseq,
            bseq,
            normalize=True,
            return_sequence=True,
        )

# Plotting
plt.rcParams["figure.figsize"] = (8, 8)
plt.imshow(overlap_matrix, cmap="inferno", aspect="auto", interpolation="none")
plt.xlabel("Behavior DataFrame Index")
plt.ylabel("SWR DataFrame Index")
plt.colorbar()
plt.tight_layout()
plt.show()
