# plb_linkee
Code for Linkee project

## Environment Setup

To get set up for this project, git clone this repo. There are two options for creating the conda environment from the command line.

### Option 1: Makefile
Run the command `make env`. 

If you need to install new packages into this environment, the environment.yaml file can be updated using the command `make env_yaml`.

### Option 2: Manual Method
Run `conda env create --prefix envs/linkee --file environment.yaml`.

Then activate into the created environment with `conda activate envs/linkee`.

Run the lines `./setup/install_packages.sh` and `python setup/download_packages.py`.

If you need to install new packages into this environment, the environment.yaml file can be updated using the following sequence of commands:

`conda env export --no-builds -p envs/linkee grep -Ev "${USER}|name|prefix" > environment.yaml`

`sed -i.bak '/pattern==/d' environment.yaml`

`sed -i.bak '/en-core-web-sm/d' environment.yaml`

`rm environment.yaml.bak`

### API Key
We use an API key for interacting with Google's Knowledge Graph functionality. You can set up a Google account to get an API key for yourself or you can ask a member of this team for the key we are using. This API key should be set up as the environment variable `GOOGLE_LINKEE_KEY` in your operating system.

## Structure of repo

- Scripts: a number of scripts holds the function used in the project
- Notebooks: interactive notebooks that can be used to run functions and generate keywords/questions/cards
- Tests: scripts that test our functions

## Other commands

- `make tests`: execute all tests in the tests folder
- `make lint`: run black and flake8 over the Python scripts to ensure they follow Python style guides.
