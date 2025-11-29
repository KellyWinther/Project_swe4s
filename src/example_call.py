from loading_utils import load_spike_data, match_times

from analysis_utils import make_correlation_dictionary
from analysis_utils import visualize_correlation_dictionary

import argparse
import sys
import os

'''
Example call (not default file):

python src/example_call.py \
    --spike_time_filename "data/full_data/7742/ \
    PartnerIntro/spike_times.npy" \
    --cluster_filename "data/full_data/7742/ \
        PartnerIntro/spike_clusters.npy" \
    --KSlabel_filename "data/full_data/7742/ \
        PartnerIntro/cluster_KSLabel.tsv" \
    --swr_filename "data/full_data/7742/ \
        PartnerIntro/7742_Partnerintro_sleepyvole_SWRs_ca2.csv"
'''


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--spike_time_filename",
        type=str,
        help="Filename (+ directory) containing spike time data",
        required=False,
        default="data/full_data/7744/PartnerIntro/spike_times.npy",
    )

    parser.add_argument(
        "--cluster_filename",
        type=str,
        help="Filename (+ directory) containing spike cluster data",
        required=False,
        default="data/full_data/7744/PartnerIntro/spike_clusters.npy",
    )

    parser.add_argument(
        "--KSlabel_filename",
        type=str,
        help="Filename (+ directory) containing KSlabel data",
        required=False,
        default="data/full_data/7744/PartnerIntro/cluster_KSLabel.tsv",
    )

    parser.add_argument(
        "--swr_filename",
        type=str,
        help="Filename (+ directory) containing SWR data",
        required=False,
        default=os.path.join(
            "data/full_data/7744/PartnerIntro",
            "7744_Partnerintro_SWRs_ca2.csv"
        ),
    )

    args = parser.parse_args()

    spike_df = load_spike_data(
        time_dir=args.spike_time_filename,
        cluster_dir=args.cluster_filename,
        label_dir=args.KSlabel_filename,
    )

    # Finds which spikes happened during a SWR
    df = match_times(
        spike_df,
        args.swr_filename,
        filter_event_data={"KSLabel": ["good"]},
        keep_event_columns=["Time", "Cluster ID"],
        progress=True,
    )

    print("First ten rows of extracted data...")
    print(df[:10])

    # Collects correlation data for neuron clusters
    corr_matrix = make_correlation_dictionary(df, normalize=False)

    # Plots the data in a 2D correlation matrix
    visualize_correlation_dictionary(corr_matrix)


if __name__ == "__main__":
    main()
