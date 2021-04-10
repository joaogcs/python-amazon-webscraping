#!/bin/bash

# install virtual environment
python3 -m pip install virtualenv

# create virtual environment
python3 -m virtualenv .venv

# activate virtual environment
source .venv/bin/activate

# install modules on virtual environment
python3 -m pip install -r requirements.txt

# run after install
# python3 -B -m scripts.run