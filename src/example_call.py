from loading_utils import load_spike_data, match_times
from analysis_utils import make_correlation_dictionary, visualize_correlation_dictionary

spike_df = load_spike_data()

# Finds which spikes happened during a SWR
df = match_times(
    spike_df,
    "../data/full_data/SWRs_7744_partner_intro.csv",
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
