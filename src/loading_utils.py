# Necessary imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import sys

def time_in_range(
        t_start: float, 
        t_end: float, 
        t: float):

    """
    Checks if a time lies between a given
    start and end time (inclusive).

    Parameters:
    -----------
    t_start :: float
        Time (seconds) marking the start of
        the window.
    t_end :: float
        Time (seconds) marking the stop of
        the window.
    t :: float
        Time (seconds) marking the time being
        compared to the provided window.

    Returns:
    --------
    in_range :: bool
        True iff t is contained within the window.
    """

    # NOTE: TypeError can be triggered by 'None'
    try:
        in_range = (t_start <= t <= t_end)
    except TypeError:
        print("Non-numeric entry provided, defaulting to 'False'")
        in_range = False

    return in_range

def load_spike_data(
        time_dir: str = "./spike_times.npy", 
        cluster_dir: str = "./spike_clusters.npy",
        label_dir: str = "./cluster_KSLabel.tsv"):

    """
    Loads the time and clusters recorded
    for each spike and joins both datasets
    into a single Pandas DataFrame.

    Parameters:
    -----------
    time_dir :: str
        Path to time data (should include the file name)
    cluster_dir :: str
        Path to cluster ID data (should include the file name)

    Returns:
    --------
    spike_df :: pd.DataFrame
        Dataframe containing spike times / IDs
    """

    try:
        spike_times = np.load(time_dir).flatten()/30000
    except FileNotFoundError:
        print(f"Filename '{time_dir}' not found")
        sys.exit(1)

    try:
        spike_clusters = np.load(cluster_dir).flatten()
    except FileNotFoundError:
        print(f"Filename '{cluster_dir}' not found")
        sys.exit(1)

    try:
        cluster_labels = pd.read_csv(label_dir, sep='\t')
    except FileNotFoundError:
        print(f"Filename '{label_dir}' not found")
        sys.exit(1)

    # Loads cluster labels ('cluster_id' renamed to match later convention)
    cluster_labels = cluster_labels.rename(columns={'cluster_id': 'Cluster ID'})

    # Joins time, id, and label data into a single array
    spike_df = pd.DataFrame({"Time":spike_times, "Cluster ID":spike_clusters})
    spike_df = pd.merge(spike_df, cluster_labels, on='Cluster ID', how='left')

    return spike_df

def match_times(
        df,
        swr_dir: str = "./SWRs_7744_partner_intro.csv", 
        progress: bool = True):

    """
    Checks if times in the user-provided DataFrame
    are contained within any of the ranges found
    in our SWR data.

    Parameters:
    -----------
    df :: pd.DataFrame
        Dataframe containing at least one column
        labelled 'Time' (units of seconds). This
        function will look for time ranges that these
        times fall between.

    progress :: bool
        Disables / enables progress bar representing
        how many times in the provided DataFrame have
        been checked.

    Returns:
    --------
    return_df :: pd.DataFrame
        A copy of the initial DataFrame, but with
        two new columns containing the SWR start
        and stop times. If no matching SWR data
        was found, both columns should default
        to NaN values.
    """

    try:
        return_df = df.copy()
    except AttributeError:
        print("Could not copy the provided DataFrame")
        sys.exit(1)

    # Loads SWR dataframe
    try:
        swr_df = pd.read_csv(swr_dir)
    except FileNotFoundError:
        assert FileNotFoundError(f"Filename '{swr_dir}' not found")
        sys.exit(1)

    # Creates columns for us to store time ranges
    return_df["SWR Start"] = np.nan
    return_df["SWR Stop"] = np.nan

    # Extracts all relevant time data (units of seconds)
    start_times = np.array(swr_df["Start"])
    stop_times = np.array(swr_df["Stop"])
    times = np.array(return_df["Time"])

    # Iterates over every time in the user-provided DataFrame
    for idx in tqdm(range(len(times)), desc="Checking SWR Data", disable=not progress):

        # Prevents excessive calculations if time falls outside of all SWR ranges
        if time_in_range(np.min(start_times), np.max(stop_times), times[idx]):

            # Adds valid SWR data to return DataFrame
            for t_start, t_stop in zip(start_times, stop_times):
                if time_in_range(t_start, t_stop, times[idx]):
                    return_df.loc[idx, "SWR Start"] = t_start
                    return_df.loc[idx, "SWR Stop"] = t_stop
                    break

    return return_df