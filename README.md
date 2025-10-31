# Can Prarie Voles Help Us Understand Memory Formation?

__Collaborators:__ Kelly, Autumn, Audrey <br>
__Last Updated:__ 10/31/2025

<img src="https://static.scientificamerican.com/sciam/cache/file/F026E019-CE84-4481-AAB758B7ECA7A10F_source.jpg?crop=16%3A9%2Csmart&w=1920" width="700em">

## Introduction
Memory formation is salient topic in modern medicinal research. Whether caused by neurodegenerative or neuropsychiatric disease, there are several medical conditions that can impact a patient's long-term memory formation. By studying patterns in memory formation in prarie voles, we may be able to uncover the neural mechanisms for generating long-lasting social memories.

One of these signals is known as a __sharp wave ripple (SWR)__, which are brief, sudden oscillatory signals produced by synchronous neuron activity. In this project, we study trends and patterns in neuron activity during SWRs. Specifically, we are interesting in studying how correlated the firing of one neuron cluster is against every other cluster, and whether the sequence in which clusters fire is consistent across many different SWR events.

(FIXME; Kelly, it would be helpful if you could check / flesh some of this introduction out? I have written out my best attempt at an explanation. Ideally, this should only be 1-2 paragraphs.)

## Retrieving the Data (FIXME)

To pull the full, original datasets, you can run the following commands in your terminal...
```
curl (FIXME) <-- Should be for loading SWR data
curl (FIXME) <-- Should be for loading spike data
curl (FIXME) <-- Should be for loading ???
```

## Repository Structure
There are three important folders in our repository...

- __/src__ ~ Stores the Python scripts used in our reducation and analysis
- __/data__ ~ Holds small subsets of data used for internal testing / example scripts
- __/test__ ~ Contains all the unit / functional test scripts

Specific descriptions of each file in these directories are provided below. However, there are also a couple that we kept in the repository's root directory. These include...

1) ```environment.yml``` ~ Has the dependency information for our project
2) ```Snakefile``` ~ The snakemake workflow used for our final reduction (FIXME; NOT MADE YET)

Any files that do not fit cleanly into the aforementioned folders will be added to the root directory.

### What's in the __\src Folder__?
The core functionality of our workflow is separated into three files...

1) ```analysis_utils.py``` ~ Responsible for building a 'correlation matrix' showing how often a given cluster fires given another cluster has also fired.
2) ```loading_utils.py``` ~ Contains three functions that are necessary for processing our data. Specifically, these functions are responsible for loading spike cluster data into a Pandas DataFrame and joining two DataFrames based on whether an 'event time' falls within a 'time window.'
3) ```raster_plot.py``` ~ (FIXME: Kelly, could you put a brief description here?)

There are also two example scripts that demonstrate example usage of these functions.

### What's in the __\data Folder__?

There are four primary types of data contained here (FIXME; will change after cleanup)...

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

### What's in the __\test Folder__ (FIXME)?