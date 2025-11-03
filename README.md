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

## Retrieving the Data
Please visit this Google Drive folder: https://drive.google.com/drive/folders/1FQuPhIkBRvUqAuGs4bC9ml2yeqDd4OmV?usp=sharing

To pull the full, original datasets, you can run the following commands in your terminal...
```
curl  """ COMING SOON """
```

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

1) ```analysis_utils.py``` ~ Responsible for building a 'correlation matrix' showing how often a given cluster fires given another cluster has also fired.
2) ```loading_utils.py``` ~ Contains three functions that are necessary for processing our data. Specifically, these functions are responsible for loading spike cluster data into a Pandas DataFrame and joining two DataFrames based on whether an 'event time' falls within a 'time window.'
3) ```raster_plot.py``` ~ Uses the data produced by 'loading_utils.py' to generate "Raster plots." Raster plots are useful for visualizing discrete data.

There are also two example scripts that demonstrate example usage of these functions. To the example script, run the following commands from the root directory...
```
cd src
python example_call.py
```
NOTE: As of now, the correlation matrix will not display when you run these commands. This is a consequence of a choice we made to create our snakemake workflow, and will be adjusted in future updates.

### What's in the __'\data' Folder__?
There are four primary types of data contained here...

1. ```spike_times.npy```
    - a 1D numpy (array? or list? will have to check) 
    - list of times an spike was found in the recording area

2. ```spike_clusters.npy```
    - a 1D numpy (again not sure array or list)
    - matches the length of spike_times, but now instead of times in the rows it has the neuron ID number.  You should expeact repeats because I have already labeled the neurons and they should spike at least 30 times, up to thousands of times, across the recording

3. ```7744_Partnerintro_events_with_indices.csv```
    - a CSV that has many columns and rows that define behavior events across the recording.  
    - the indicies match the spike times (need to be sure to select the right column because the alignment for the video time stamps isn't right. there were some dropped frames which are now corrected to get near perfect aligment with the new time index)

4. ```SWRs_7744_partner_intro.csv```
    - sharp wave ripple csv with start and stop times of each detected ripple. 
    - also includes some ripple features: 
            - duration
            - max signal envelope amplitude

We have a variety of filetypes (i.e., .npy, .csv, .tsv) for now, but we are working on reducing our data into a single, consistent type. If you look in the '\data' folder, you will see two sub-folders labelled '\test_data' and 'full_data'. The first of these sub-folders holds short, sample versions of our data that we can use for quick testing. The second sub-folder contains the raw, complete datasets we are using for our analysis. Until we get the ```curl``` command working, these files are provided on the repository.

### What's in the __'\test' Folder__ (FIXME)?
