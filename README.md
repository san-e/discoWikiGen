# discoWikiGen
WIP dynamic wiki page source generator for Discovery Freelancer

## Installation

### Linux
Run `venv.sh`. This assumes you have the `uv` package manager installed. Refer to installation instructions [here](https://docs.astral.sh/uv/getting-started/installation/).

### Windows

Create a virtual environment if you feel like it. 
Navigate to the `requirements.txt` file and run `pip install -r requirements.txt`.

## Usage
Run `scripts/main.py`. It will guide you through initial setup.
If you want to render ship images, you will need to provide paths to a Librelancer SDK install and a Blender install.
    

---
## Dependencies
- My [fork](https://github.com/BASEFlow1/flint) of [flint](https://github.com/biqqles/flint)
- beautifulsoup4
- pillow
- html-table-parser-python3
- pandas
- alive_progress
- requests
- selenium
- opencv-python

Developed and tested on Python 3.14.0
