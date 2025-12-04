
"""
Sequence Overlap Analysis

This script:
1. Loads spike data, behavior windows, and SWR windows.
2. Computes cluster-ID sequences per window.
3. Calculates normalized overlap using Rabin Karp LCCS.
4. Produces a heatmap of SWR behavior overlaps.
"""

import argparse
import sys

from loading_utils import group_dataframes_by_time
from sequence_matching_utils import (
    build_file_paths,
    load_data,
    preprocess_behavior_df,
    compute_overlap_matrix,
    plot_overlap_matrix,
)


def parse_arguments():

    parser = argparse.ArgumentParser(
        description="Compute SWR–behavior overlap matrices."
    )

    parser.add_argument(
        "--individual",
        type=str,
        required=True,
        help="Individual ID ('7742', '7744', or 'test').",
    )

    parser.add_argument(
        "--stimuli",
        type=str,
        required=False,
        help="Social stimuli folder name for full data.",
        default="PartnerIntro",
    )

    args = parser.parse_args()

    if args.individual not in ["7742", "7744", "test"]:
        print("Error: individual must be '7742', '7744', or 'test'.")
        sys.exit(1)

    if args.stimuli not in ["PartnerIntro", "SSIntro"]:
        print("Error: stimuli must be 'PartnerIntro' or 'SSIntro'.")
        sys.exit(1)

    return args


def main():
    args = parse_arguments()
    paths = build_file_paths(args.individual, args.stimuli)

    spike_df, behavior_df, swr_df = load_data(paths)
    behavior_df = preprocess_behavior_df(behavior_df)

    behavior_clusters = group_dataframes_by_time(
        window_df=behavior_df,
        event_df=spike_df,
        event_time_column="Time",
        keep_event_columns=["Cluster ID"],
        time_interval_columns=["Start", "Stop"],
        progress=True,
    )

    swr_clusters = group_dataframes_by_time(
        window_df=swr_df,
        event_df=spike_df,
        event_time_column="Time",
        keep_event_columns=["Cluster ID"],
        time_interval_columns=["Start", "Stop"],
        progress=True,
    )

    overlap = compute_overlap_matrix(
        behavior_clusters["Event Cluster IDs"].tolist(),
        swr_clusters["Event Cluster IDs"].tolist(),
    )

    plot_overlap_matrix(overlap)


if __name__ == "__main__":
    main()
