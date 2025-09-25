# Project_swe4s
This repo contains code and necessary data for Kelly, Autumn, and Audrey's Software Engineering for Scientists Project (SWE4S) Fall 2025

**Documents:**
1. spike_times.npy 
    - a 1D numpy (array? or list? will have to check) 
    - list of times an spike was found in the recording area

2. spike_clusters.npy
    - a 1D numpy (again not sure array or list)
    - matches the length of spike_times, but now instead of times in the rows it has the neuron ID number.  You should expeact repeats because I have already labeled the neurons and they should spike at least 30 times, up to thousands of times, across the recording

3. 7744_Partnerintro_events_with_indices.csv
    - a CSV that has many columns and rows that define behavior events across the recording.  
    - the indicies match the spike times (need to be sure to select the right column because the alignment for the video time stamps isn't right. there were some dropped frames which are now corrected to get near perfect aligment with the new time index)

4. SWRs_7744_partner_intro.csv
    - sharp wave ripple csv with start and stop times of each detected ripple. 
    - also includes some ripple features: 
            - duration
            - max signal envelope amplitude
            