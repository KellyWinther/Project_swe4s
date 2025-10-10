import numpy as np
import matplotlib.pyplot as plt

# === PARAMETERS ===
SWR_index = 1 # Select which trial to visualize

# Choose region (replace MOs_mask with your own boolean mask)
spikes_index = spike_times[SWR_mask]       # spikes that occur during SWRs

# === Extract start and end times for selected trial ===
plot_start = SWR_start
plot_end   = SWR_end

# === Filter spike times within this trial ===
within_interval_mask = (spikes_index >= plot_start) & (spikes_index <= plot_end)
filtered_spike_times = spikes_index[within_interval_mask]
filtered_neuron_ids  = neuron_id_number_per_spike_times[within_interval_mask]

# === Unique neuron IDs for plotting ===
unique_neurons = np.unique(filtered_neuron_ids)

# === Create raster plot ===
plt.figure(figsize=(10, 6))
for i, neuron_id in enumerate(unique_neurons, start=1):
    neuron_spike_times = filtered_spike_times[filtered_neuron_ids == neuron_id]
    y_values = np.ones_like(neuron_spike_times) * i
    for t in neuron_spike_times:
        plt.plot([t, t], [i - 0.4, i + 0.4], color='k', linewidth=1)

# === Region name for title ===
region_name = region_index_str.split('_')[0]

plt.xlabel('Time (s)')
plt.ylabel('Neuron Index')
plt.title(f'Raster Plot for {SWR_index} SWR')
plt.ylim(0, len(unique_neurons) + 1)
plt.tight_layout()
plt.show()
