# PSL-KGE

An integration of embedding techniques into Probablistic Soft Logic (PSL). Traditionally, PSL does not natively handle such an integration, and therefore this project aims to treat embedding dimensions as latent features and creating rules describing the relations between each dimension.

# Data

We use FB15k and WN18 which is published in "Translating Embeddings for Modeling Multi-relational Data (2013)." by Bordes et al. [link](https://www.hds.utc.fr/everest/doku.php?id=en:transe)

# Settings

All settings are located in the config.json file. 

splits:              Number of splits to be generated

percent_train:       % of dataset to be allocated to training data  

seed:                Seed for the pseudo-random number generator  

false_triples_ratio: Number of false triples to be generated for each valid triple  

Dataset:             Name of the Dataset folder  

data:                Path to the dataset file  

dimensions:          Number of Dimesions  

type_split:          Method used for splitting the data (currently only random is set)  

map_input:           Setting to have eval.sh map input from the original dataset to the PSL representation

# Instructions

Download or clone the project

Call gen_splits.sh with config.json as the only argument to generate splits

./gen_splits.sh config.json

Call run.sh with a name for the output

./run.sh results_directory

Alternatively, call prepare_psl.sh with config.json as the only argument to convert the data into PSL form

./prepare_psl.sh config.json

Then call run.sh located in the /psl/cli folder to run psl on the project

./psl/cli/run.sh

Finally, call eval.sh with config.json

./psl/cli/run.sh config.json
