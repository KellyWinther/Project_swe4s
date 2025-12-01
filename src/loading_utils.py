# Necessary imports
import numpy as np
import pandas as pd
from tqdm import tqdm
import sys


def time_in_range(
    t_start: float,
    t_end: float,
    t: float,
) -> bool:
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
    time_dir: str,
    cluster_dir: str,
    label_dir: str,
) -> pd.DataFrame:
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
    label_dir :: str
        Path to the KSLabel data (should include the file name)

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
    cluster_labels = cluster_labels.rename(
        columns={"cluster_id": "Cluster ID"}
    )

    # Joins time, id, and label data into a single array
    spike_df = pd.DataFrame(
        {"Time": spike_times, "Cluster ID": spike_clusters}
    )
    spike_df = pd.merge(spike_df, cluster_labels, on="Cluster ID", how="left")

    return spike_df


def filter_dataframe(
    df: pd.DataFrame,
    filter_dictionary: dict,
) -> pd.DataFrame:
    """
    Attempts to filter down a DataFrame for a handful
    of columns with user-specified "allowed values".
    For example, if you wanted to filter a DataFrame
    based on the "KSLabel" column, the 'filter_dictionary'
    may look like...

        {"KSLabel": ["good",]}

    If an empty dictionary is provided, then no filter will
    be applied.

    Parameters:
    -----------
    df :: pd.DataFrame
        A DataFrame to filter down based on the value(s) of
        a specified column(s).
    filter_dictionary :: dict
        Specifies which column to filter by (should be a
        key in the dictionary) and what values should be
        kept (should be a list of entries).

    Returns:
    --------
    df :: pd.DataFrame
        The final, filtered DataFrame.
    """

    for column_name, valid_values in filter_dictionary.items():

        try:
            df = df[df[column_name].isin(valid_values)]

        # Should only trigger if a user-provided column is not in df
        except KeyError:
            print(
                f"Column '{column_name}' not found",
                "moving on without filtering.",
            )

        # Should only trigger if the value of filter dictionary is not a list
        except TypeError:
            print(
                f"Valid values must be a list, not '{type(valid_values)}'",
                "Moving on without filtering.",
            )

    return df


def group_dataframes_by_time(
    window_df: pd.DataFrame,
    event_df: pd.DataFrame,
    event_time_column: str,
    keep_event_columns: list,
    time_interval_columns: list,
    progress: bool,
) -> pd.DataFrame:
    """
    Checks if events contained in a user-provided DataFrame
    contain times that fall within a window found in a
    separate DataFrame. For consistency, the DataFrame containing
    a single time per row is referred to as the 'event dataframe',
    and the DataFrame containing two times (start and stop of a
    window) is referred to as the 'window dataframe'.

    Parameters:
    -----------
    window_df :: pd.DataFrame
        Dataframe containing at least one column
        labeled 'Time' (or the string assigned to
        'event_time_column'; assumes units of seconds).
        This function will look for time ranges that
        these times fall between.
    event_df :: pd.DataFrame
        Dataframe containing at least one column
        labeled 'Time' (or the string assigned to
        'event_time_column'; assumes units of seconds).
        This function will look for time ranges that
        these times fall between.
    event_time_column :: str
        The name of a column in the 'event dataframe' containing
        time data (assumes units of seconds).
    keep_event_columns :: list
        A list of columns to keep from the 'event dataframe'. For
        example, if provided ['A', 'B'], then the values of 'A' and
        'B' for all matched events will be saved in a list in the
        returned dataframe.
    time_interval_column :: list
        The names of two columns in the 'window dataframe'
        containing the start and stop (both in seconds) of
        a valid window. Events with a time falling between these
        two values will be associated with the respective window.
    progress :: bool
        Disables / enables progress bar.

    Returns:
    --------
    grouped_df :: pd.DataFramed
        A copy of the 'window_df' where new columns have been
        created for each event found within a given window.
    """

    # Prevents us from replacing initial DataFrame
    grouped_df = window_df.copy()

    # Renames columns to be grammatically correct
    renamed_event_columns = [
        f"Event {string}s" for string in keep_event_columns
    ]

    # Initialize new columns properly (object dtype) to prevent Pandas errors
    for col in renamed_event_columns:
        grouped_df[col] = None
        grouped_df[col] = grouped_df[col].astype("object")

    # Extract all relevant time data (units of seconds)
    event_times = np.array(event_df[event_time_column])

    for idx in tqdm(
        range(len(grouped_df)),
        desc="Checking Event Data",
        disable=not progress,
    ):

        # Masking allows us to avoid excessive looping
        start_time = np.array(grouped_df[time_interval_columns[0]])[idx]
        end_time = np.array(grouped_df[time_interval_columns[1]])[idx]
        mask = (start_time <= event_times) & (event_times <= end_time)

        for column, renamed_column in zip(
            keep_event_columns, renamed_event_columns
        ):
            data = list(event_df[column][mask])
            grouped_df.at[idx, renamed_column] = data

    return grouped_df


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

    # If filter dictionary is empty, DataFrame is not modified
    event_df = filter_dataframe(event_df, filter_event_data)
    window_df = filter_dataframe(window_df, filter_window_data)

    grouped_df = group_dataframes_by_time(
        window_df=window_df,
        event_df=event_df,
        event_time_column=event_time_column,
        keep_event_columns=keep_event_columns,
        time_interval_columns=time_interval_columns,
        progress=progress,
    )

    return grouped_df
