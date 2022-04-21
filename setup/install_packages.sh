#!/bin/bash

#Install two packages that can not be installed by yaml
pip install git+https://github.com/uob-vil/pattern.git
python3 -m spacy download en_core_web_sm
