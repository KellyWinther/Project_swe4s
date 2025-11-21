# Can Prarie Voles Help Us Study Memory Formation?

__Collaborators:__ Kelly, Autumn, Audrey<br>
__Last Updated:__ 10/31/2025

<img src="https://static.scientificamerican.com/sciam/cache/file/F026E019-CE84-4481-AAB758B7ECA7A10F_source.jpg?crop=16%3A9%2Csmart&w=1920" width="700em">

## Introduction
Memory formation is salient topic in modern medical research. Whether caused by neurodegenerative or neuropsychiatric disease, there are several medical conditions that can impact a patient's long-term memory formation. By studying patterns in memory formation in prairie voles, a unique rodent species that forms complex social relationships, we may be able to uncover the neural mechanisms for generating long-lasting social memories.

One of these signals is known as a __sharp wave ripple (SWR)__, which is a brief oscillatory event produced by synchronous neuron activity and vital to memory consolidation. The neuronal activity within a SWR for spatial memories is a sequential replay of neuronal firing that recapitulates the exact event being converted to a memory. In this project, we investigate neuron activity during SWRs following social interactions. Specifically, we are interested in identifying whether SWRs for social memories similarly maintain sequential patterns, or whether a specific set of neurons are sufficient to encode a social memory without maintaining a set firing order. 

Important Notes and Scientific Considerations:
When processing SWR data, a single neuron is identified by its 'cluster id' and a single unit of activity is called a 'spike'.
Neurons come in a variety of types that play different roles in the biological system. Specifically, pyramidal neurons are known to maintain sequences in replay events. 


## Quickstart
If you would like to re-create our analysis, you can clone our respository by running...
```
git clone https://github.com/KellyWinther/Project_swe4s.git
```
Then, to run our snakemake workflow, simply run...
```
cd Project_swe4s
snakemake --cores 1
```
This will create an 'outputs/' folder in the root directory with some intermediate data products. As of now, the primary result is the ```correlation_matrix.png``` that shows how correlated neuron clusters are when they fire. If you are having trouble getting the workflow to run, try using the ```environment.yml``` file we provided!

## Repository Structure
There are three important folders in our repository...

- __/src__ ~ Stores the Python scripts used in our reducation and analysis
- __/data__ ~ Holds the data used for internal testing / example scripts and our full analysis
- __/test__ ~ Contains all the unit / functional test scripts

Specific descriptions of each file in these directories are provided below. However, there are also a couple that we kept in the repository's root directory. These include...

1) ```environment.yml``` ~ Has the dependency information for our project
2) ```Snakefile``` ~ The snakemake workflow used for our final reduction

Any files that do not fit cleanly into the aforementioned folders will be added to the root directory.

### What's in the __'\src' Folder__?
The core functionality of our workflow is separated into three files...

1) ```analysis_utils.py``` ~ Responsible for:
    - building a 'correlation matrix' showing how often a given cluster fires given another cluster has also fired.
    - building histograms from circularly permuted shifts of SWR start times to assess whether a neuron cluster spikes within a ripple time more often than expected. 

2) ```loading_utils.py``` ~ Contains three functions that are necessary for processing our data. Specifically, these functions are responsible for loading spike cluster data into a Pandas DataFrame and joining two DataFrames based on whether an 'event time' falls within a 'time window.'

3) ```raster_plot.py``` ~ Uses the data produced by 'loading_utils.py' to generate "Raster plots." Raster plots are useful for visualizing discrete spiking data. These are scatter plots used in neuroscience to visualize the timing of action potentials (spikes) from one or more neurons over time. Each row in the plot represents a single neuron, and each vertical line represents a spike at a specific time point. This visualization allows researchers to see patterns in neural activity and how it relates to specific stimuli or task. Our plots are spiking activity, where time on the x-axis is relative to the peak frequency of the sharp wave ripple. Around it's peak, the SWR often has the greatest number of co-active neurons. 

There are also two example scripts that demonstrate example usage of these functions. To the example script, run the following command from the root directory...
```
python src/example_call.py
```
NOTE: As of now, the correlation matrix will not display when you run these commands. This is a consequence of a choice we made to create our snakemake workflow, and will be adjusted in future updates.

### What's in the __'\data' Folder__?
There are four primary types of data contained here...

1. ```spike_times.npy```
    - a 1D numpy array
    - list of times an spike was found in the recording area

2. ```spike_clusters.npy```
    - a 1D numpy array
    - matches the length of spike_times, but now instead of times in the rows it has the cluster ID number. Biologically speaking, a cluster ID represents a single neuron. 

3. ```clusterKSLabel.tsv```
    - a 2D array with the cluster ID number and a judgement on how good of a recording we attained from that cluster. 
    options are "good" or "mau"
    - "good" the cluster ID is likely one single neuron's activity
    - "mau" the cluster ID is likely a mixture of neuron activity and not a clean representation of any single neuron. 

4. ```Animal#_SocialType_events_with_indices.csv```
    example: "7744_SSintro_events_with_indices.csv"
    - Social Type represents what social interaction the animal expeienced in that recording. Options are "PartnerIntro" or "SSIntro".
          - Partner Intro is the introduction to an novel opposite sex animal
          - SS Intro is the introduction to a novel same-sex animal. 
    - This is a CSV that defines behavior events across the recording. Examples: sleeping, social interaction, etc. Including there start and stop times and other details like duration. This CSV is autogenerated output by BORIS animal behvaior labeling software. 
    - the time indicies in the columns "indexStart" and "indexEnd" match the spike times after you adjust for the camera sampling rate of 2500. Meaning the index must be divided by 2500 to get to seconds and align to spike times. 

5. ```Animal#_SocialType_SWRs_BrainRegion.csv```
    example: "7744_SSintro_SWRs_ca2.csv"
    - sharp wave ripple csv with start and stop times of each detected ripple. 
    - also includes some ripple features: 
            - ripple peak time
            - duration
            - max envelope amplitude of the signal (using the hilbert transformation)
    - brain region label "ca2" is hippocampal subregion CA2


If you look in the '\data' folder, you will see two sub-folders labelled '\test_data' and 'full_data'. The first of these sub-folders holds short, sample versions of our data that we can use for quick testing. 

### What's in the __'\test' Folder__?
Here you can find the scripts we use for automated testing. These are broken up into "functional tests" and "unit tests." We intend to increase the scope of these tests in the near future.