from loading_utils import load_spike_data, match_times

spike_df = load_spike_data()

df = match_times(spike_df, progress=True)

print("First ten rows of extracted data...")
print(df[:10])