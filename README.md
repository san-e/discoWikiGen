# flWiki
Very WIP dynamic wiki page source generator for Discovery Freelancer 

The idea as of right now is to dump everything I can into one file and using that to build a wiki page later on.

## Dependencies
- My [fork](https://github.com/BASEFlow1/flint) of [flint](https://github.com/biqqles/flint)
- pyperclip

To install, do:

`pip install pyperclip`

`pip install https://github.com/baseflow1/flint/archive/master.zip -U`

or navigate to the `requirements.txt` file and do `pip install -r requirements.txt`

## Usage
1. `git clone` this repo into a directory of your choosing
2. Run `flWikiGen.py [path_to_freelancer]`
3. Run `pageGen.py` in the same directory

The page source for the ship you selected will be pasted into your clipboard.

---
Developed and tested on Python 3.10.4
