# install virtual environment
python3 -m pip install virtualenv

# create virtual environment
python3 -m virtualenv .venv

# activate virtual environment
.venv\Scripts\activate.ps1

# install modules on virtual environment
python3 -m pip install -r requirements.txt

# run after install
# python3 -B -m scripts.run

# pause