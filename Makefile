SHELL=/bin/bash

#######
# Set up work area

LOCAL_WORKDIR ?= ${PWD}/local_workdir
LOCAL_DATADIR ?= ${PWD}/local_datadir
ENVS_DIR = ./envs

${LOCAL_WORKDIR}:
	mkdir -p ${LOCAL_WORKDIR}

${LOCAL_DATADIR}:
	mkdir -p ${LOCAL_DATADIR}

${ENVS_DIR}:
	mkdir -p ${ENVS_DIR}

#######
# Set up conda environment

MODEL_ENV_NAME = linkee
MODEL_ENV_YAML ?= environment.yaml
MODEL_ENV = ${ENVS_DIR}/${MODEL_ENV_NAME}
MODEL_ENV_PYTHON ?= $(shell source ${BASE_CONDA}/etc/profile.d/conda.sh\
		&& conda activate ${MODEL_ENV} && which python)

BASE_CONDA = $(shell conda info --base)

ENV_VARIABLES := PYTHONPATH=${PYTHONPATH}:${PWD} \
		LOCAL_WORKDIR=${LOCAL_WORKDIR} \
		LOCAL_DATADIR=${LOCAL_DATADIR}

env: | ${MODEL_ENV}
${MODEL_ENV}: | ${ENVS_DIR}
	PIP_REQUIRE_VIRTUALENV=0 conda env create --prefix ${MODEL_ENV} -f ${MODEL_ENV_YAML} --insecure
	source ${BASE_CONDA}/etc/profile.d/conda.sh &&
	conda activate ${MODEL_ENV} && python -m ipykernel install --user --name ${MODEL_ENV_NAME} \
	./setup/install_packages.sh \
	python setup/download_packages.py 

env_yaml:
	source ${BASE_CONDA}/etc/profile.d/conda.sh && \
	conda activate ${MODEL_ENV} && \
	conda env export --no-builds -p ${MODEL_ENV} \
	| grep -Ev "${USER}|name|prefix" > ${MODEL_ENV_YAML}


#######
# Abbreviations for common sequences

RUN_IN_CONDA_ENV = source ${BASE_CONDA}/etc/profile.d/conda.sh && \
		conda activate ${MODEL_ENV} && \
		env ${ENV_VARIABLES} \

######
# Testing

tests: ${LOCAL_WORKDIR}
	${RUN_IN_CONDA_ENV} \
	pytest tests/

######
# Linting

lint:
	source ${BASE_CONDA}/etc/profile.d/conda.sh && \
	conda activate ${MODEL_ENV} && \
	black scripts/ tests/ --line-length=79 && \
	flake8 scripts/ tests/ --ignore=E402,E501,W503,E203,E231,W605

######
# Other

list:
	@LC_ALL=C $(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null |\
	awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' |\
	sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

.PHONY: \
	env \
	env_yaml \
	tests \
	lint \
	list
