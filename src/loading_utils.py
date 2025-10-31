# Necessary imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import sys


def time_in_range(t_start: float, t_end: float, t: float):
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
        in_range = t_start <= t <= t_end
    except TypeError:
        print("Non-numeric entry provided, defaulting to 'False'")
        in_range = False

    return in_range


def load_spike_data(
    time_dir: str = "./spike_times.npy",
    cluster_dir: str = "./spike_clusters.npy",
    label_dir: str = "./cluster_KSLabel.tsv",
):
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

    # Factor of 30,000 accounts for sampling rate
    try:
        spike_times = np.load(time_dir).flatten() / 30000
    except FileNotFoundError:
        print(f"Filename '{time_dir}' not found")
        sys.exit(1)

    # The '.flatten()' command fixes the data loading as a column
    try:
        spike_clusters = np.load(cluster_dir).flatten()
    except FileNotFoundError:
        print(f"Filename '{cluster_dir}' not found")
        sys.exit(1)

    try:
        cluster_labels = pd.read_csv(label_dir, sep="\t")
    except FileNotFoundError:
        print(f"Filename '{label_dir}' not found")
        sys.exit(1)

    # Loads cluster labels ('cluster_id' renamed to match later convention)
    cluster_labels = cluster_labels.rename(columns={"cluster_id": "Cluster ID"})

    # Joins time, id, and label data into a single array
    spike_df = pd.DataFrame({"Time": spike_times, "Cluster ID": spike_clusters})
    spike_df = pd.merge(spike_df, cluster_labels, on="Cluster ID", how="left")

    return spike_df


def match_times(
    dataframe: pd.DataFrame,
    directory: str,
    filter_event_data: dict = {},
    filter_window_data: dict = {},
    event_time_column: str = "Time",
    time_interval_columns: list = ["Start", "Stop"],
    keep_event_columns: list = [],
    progress: bool = True,
) -> pd.DataFrame:
    """
    Checks if events contained in a user-provided DataFrame
    contain times that fall within a window found in a
    separate datafile. For consistency, the user-provided
    DataFrame is referred to as the 'event dataframe' and
    should only contain a single time per row. The directory
    should point towards the 'window dataframe' which should
    contain two times per row (a start and stop time).

    Parameters:
    -----------
    dataframe :: pd.DataFrame
        Dataframe containing at least one column
        labeled 'Time' (or the string assigned to
        'event_time_column'; assumes units of seconds).
        This function will look for time ranges that
        these times fall between.
    directory :: str
        Path (directory + filename) containing data with
        times ranges (found in columns 'Start' and 'Stop'
        by default).
    filter_event_data :: dict
        Indicates which values to filter by in the 'event
        dataframe.' Every key-value pair should be a column
        name in the 'event dataframe' (key) and a list of
        valid entries (value). If no arguments are provided,
        then no filtering is applied.
    filter_window_data :: dict
        Indicates which values to filter by in the 'window
        dataframe.' Every key-value pair should be a column
        name in the 'window dataframe' (key) and a list of
        valid entries (value). If no arguments are provided,
        then no filtering is applied.
    event_time_column :: str
        The name of a column in the 'event dataframe' containing
        time data (assumes units of seconds).
    time_interval_column :: list
        The names of two columns in the 'window dataframe'
        containing the start and stop (both in seconds) of
        a valid window. Events with a time falling between these
        two values will be associated with the respective window.
    keep_event_columns :: list
        A list of columns to keep from the 'event dataframe'. For
        example, if provided ['A', 'B'], then the values of 'A' and
        'B' for all matched events will be saved in a list in the
        returned dataframe.
    progress :: bool
        Disables / enables progress bar.

    Returns:
    --------
    return_df :: pd.DataFrame
        A copy of the initial DataFrame, but with
        two new columns containing the SWR start
        and stop times. If no matching SWR data
        was found, both columns should default
        to NaN values.
    """

    # This prevents us from accidentally modifying the original DataFrame
    try:
        event_df = dataframe.copy()
    except AttributeError:
        print("Could not copy the provided DataFrame")
        sys.exit(1)

    try:
        window_df = pd.read_csv(directory)
    except FileNotFoundError:
        assert FileNotFoundError(f"Filename '{directory}' not found")
        sys.exit(1)

    # NOTE: These could probably be broken off into a separate function, will revisit later
    for column_name, valid_values in filter_event_data.items():
        try:
            event_df = event_df[event_df[column_name].isin(valid_values)]
        except KeyError:
            print(f"Column name '{column_name}' not found, moving on without filtering")
        except TypeError:
            print(f"Valid values must be a list, not '{type(valid_values)}'")

    for column_name, valid_values in filter_window_data.items():
        try:
            window_df = window_df[window_df[column_name].isin(valid_values)]
        except KeyError:
            print(f"Column name '{column_name}' not found, moving on without filtering")
        except TypeError:
            print(f"Valid values must be a list, not '{type(valid_values)}'")

    # Renames columns to be grammatically correct
    renamed_event_columns = [f"Event {string}s" for string in keep_event_columns]

    # Initialize new columns properly (object dtype) to prevent Pandas errors
    for col in renamed_event_columns:
        window_df[col] = None
        window_df[col] = window_df[col].astype("object")

    # Extract all relevant time data (units of seconds)
    event_times = np.array(event_df[event_time_column])

    for idx in tqdm(
        range(len(window_df)), desc="Checking Event Data", disable=not progress
    ):

        # Masking allows us to avoid excessive looping
        start_time = np.array(window_df[time_interval_columns[0]])[idx]
        end_time = np.array(window_df[time_interval_columns[1]])[idx]
        mask = (start_time <= event_times) & (event_times <= end_time)

        # NOTE: Apparently Pandas is depricating their old indexing tricks, need to use '.at' now
        for column, renamed_column in zip(keep_event_columns, renamed_event_columns):
            data = list(event_df[column][mask])
            window_df.at[idx, renamed_column] = data

    return window_df
