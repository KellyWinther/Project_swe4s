import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from loading_utils import load_spike_data, match_times
from raster_plot_utils import prep_raster, select_ripples_to_plot, plot_raster

'''
Generate ripple-aligned raster plots from spike data.

example usage:
python3 make_raster.py \
    --spike_time ".../spike_times.npy" \
    --clusters ".../spike_clusters.npy" \
    --kslabels ".../cluster_KSLabel.tsv" \
    --swr_csv ".../7744_Partnerintro_SWRs_ca2.csv" \
    --window 0.25 \
    --color black \
    --tick_width 3 \
    --height 9 \
    --width 6 \
    --ripple_index 111
'''


def build_parser():
    parser = argparse.ArgumentParser(
        description="Generate ripple-aligned raster plots from spike data."
    )

    parser.add_argument(
        "--spike_time",
        type=str,
        required=True,
        help="Path to spike_times.npy"
    )

    parser.add_argument(
        "--clusters",
        type=str,
        required=True,
        help="Path to spike_clusters.npy"
    )

    parser.add_argument(
        "--kslabels",
        type=str,
        required=True,
        help="Path to cluster_KSLabel.tsv"
    )

    parser.add_argument(
        "--swr_csv",
        type=str,
        required=True,
        help="Path to SWR CSV file (with Peak, Start, Stop columns)."
    )

    parser.add_argument(
        "--ripple_index",
        type=int,
        nargs="*",
        default=None,
        help="Optional ripple index or multiple indices (space-separated). "
             "If omitted, all ripples are plotted."
    )

    parser.add_argument(
        "--window",
        type=float,
        default=0.25,
        help="Window size in sec. (±window around ripple peak). Default=0.25",
    )

    parser.add_argument(
        "--height",
        type=float,
        default=9,
        help="Height of raster figure"
    )

    parser.add_argument(
        "--width",
        type=float,
        default=6,
        help="Width of raster figure"
    )

    parser.add_argument(
        "--tick_width",
        type=float,
        default=3,
        help="Marker size for spike events"
    )

    parser.add_argument(
        "--color",
        type=str,
        default="black",
        help="Spike color"
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    print("\n 1. Loading spike data")
    spike_df = load_spike_data(
        time_dir=args.spike_time,
        cluster_dir=args.clusters,
        label_dir=args.kslabels,
    )

    print(" 2. Matching spikes to SWRs")
    df = match_times(
        spike_df,
        args.swr_csv,
        filter_event_data={"KSLabel": ["good"]},
        keep_event_columns=["Time", "Cluster ID"],
        progress=True,
    )

    print("\n--- match_times() OUTPUT ---")
    print(df.head(4))
    # print(df.columns)  # Uncomment to see column names

    print(" 3. Preparing raster data (exploding spikes)")
    exp_df = prep_raster(df)

    print(" 4. Selecting ripples to plot")
    exp_df_sel = select_ripples_to_plot(exp_df, ripple_index=args.ripple_index)

    print(" 5. Plotting raster")
    plot_raster(
        exp_df_sel,
        height=args.height,
        width=args.width,
        color=args.color,
        tick_width=args.tick_width,
        window=args.window
    )


if __name__ == "__main__":
    main()
