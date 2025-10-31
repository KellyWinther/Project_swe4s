import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt


def make_correlation_dictionary(
    df: pd.DataFrame,
    id_column_name: str = "Event Cluster IDs",
    normalize: bool = True,
):
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
                corr_dict[baseline_id][compared_id] /= baseline_value

    return corr_dict


def visualize_correlation_dictionary(corr_matrix):
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
    """

    # Initializes grid with zeros in case no information is found for an id
    shape = (len(corr_matrix), len(corr_matrix))
    grid = np.zeros(shape)

    keys = list(corr_matrix.keys())

    # Populates matrix with values found in the dictionary
    # NOTE: I think I have the indexing order right, but another pair of eyes would be great!
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
    plt.show()
