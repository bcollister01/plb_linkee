# plb_linkee
Code for Linkee project

## Environment Setup

To get set up for this project, git clone this repo. To create the conda environment, while within the repo on the command line, run the command `make env` or `conda env create --prefix envs/linkee --file environment.yaml`. You will also need to pip install a couple of things separately within the notebook (pattern and en_core_web_sm). 

If you need to install new packages into this environment, the environment.yaml file can be updated using the command `make env_yaml` (currently, you will need to go in and delete the lines relating to pattern and en_core_web_sm). 

## Structure of repo

- Scripts: a number of scripts holds the function used in the project
- Notebooks: interactive notebooks that can be used to run functions and generate keywords/questions/cards
- Tests: scripts that test our functions

## Other commands

- `make tests`: execute all tests in the tests folder
- `make lint`: run black and flake8 over the Python scripts to ensure they follow Python style guides.
