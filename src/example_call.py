from loading_utils import load_spike_data, match_times

spike_df = load_spike_data()

df = match_times(spike_df, progress=True)

print("First ten rows of extracted data...")
print(df[:10])

from analysis_utils import *

# Collects correlation data for neuron clusters
corr_matrix = make_correlation_dictionary(df, normalize=False)

# Plots the data in a 2D correlation matrix
visualize_correlation_dictionary(corr_matrix)