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
2. Change the `[path_to_disco]` string in `databaseGen.bat` to the path to your Discovery installation. (Remember to re-do this step everytime a patch hits.)
3. Run `databaseGen.bat`
4. Now run `pageGen.bat` in the same directory.
![pageGen.bat in use](/repository/images/pageGen.png?raw=true "pageGen.bat in use")

The page source for the ship you selected will be pasted into your clipboard.

---
Developed and tested on Python 3.10.4
