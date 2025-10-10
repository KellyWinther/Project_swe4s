# Project_swe4s
This repo contains code and necessary data for Kelly, Autumn, and Audrey's Software Engineering for Scientists Project (SWE4S) Fall 2025

**src folder**
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

5. Raster_plot.py
    - basic structure of python code to make a raster plot. Not complete as of 10.10.2025

            
**test_data**
- In this folder you will find two data sets to use for unit tests. 
    1. "_int" : files with underscore int are test datasets that only include integers and no floats

    2. test_data files without "_int" have floats

- to view the npy's as csv, I have added the npy_to_csv.py and the output is saved in the folder "npy_as_csv". This is useful for copy and pasting the expected data during  unit testing. 

- behavior test data set with a simplified .csv is saved as "test_7744_Partnerintro.csv"
