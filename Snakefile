import os
import sys
import pandas as pd

try:
    os.mkdir("outputs")
except FileExistsError:
    pass

sys.path.append("src/")  # noqa

import loading_utils  # noqa
import analysis_utils

rule all:
    input:
        "outputs/correlation_matrix.png"

rule load_spike_data:
    output:
        "outputs/spike_data.csv"
    run:
        df = loading_utils.load_spike_data(
                time_dir = "data/full_data/spike_times.npy",
                cluster_dir  = "data/full_data/spike_clusters.npy",
                label_dir = "data/full_data/cluster_KSLabel.tsv",
        )
        df.to_csv("outputs/spike_data.csv", index=False)

rule match_spikes_with_SWRs:
    input:
        "outputs/spike_data.csv"
    output:
        "outputs/matched_SWR_data.csv"
    run:
        spike_df = pd.read_csv("outputs/spike_data.csv")
        df = loading_utils.match_times(
                spike_df,
                "data/full_data/SWRs_7744_partner_intro.csv",
                filter_event_data={"KSLabel": ["good"]},
                keep_event_columns=["Time", "Cluster ID"],
        )
        df.to_csv("outputs/matched_SWR_data.csv", index=False)

rule generate_correlation_matrix:
    input:
        "outputs/matched_SWR_data.csv"
    output:
        "outputs/correlation_matrix.png"
    run:
        spike_df = pd.read_csv("outputs/spike_data.csv")
        df = loading_utils.match_times(
                spike_df,
                "data/full_data/SWRs_7744_partner_intro.csv",
                filter_event_data={"KSLabel": ["good"]},
                keep_event_columns=["Time", "Cluster ID"],
        )

        corr_dictionary = analysis_utils.make_correlation_dictionary(
            df,
            normalize=False,
        )

        analysis_utils.visualize_correlation_dictionary(
            corr_dictionary,
            save_directory="outputs/correlation_matrix.png",
        )