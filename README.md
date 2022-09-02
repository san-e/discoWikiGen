# discoWikiGen
WIP dynamic wiki page source generator for Discovery Freelancer 


## Dependencies
- My [fork](https://github.com/BASEFlow1/flint) of [flint](https://github.com/biqqles/flint)
- pyperclip
- beautifulsoup4
- html-table-parser-python3
- pandas
- alive_progress

To install, do:

`pip install pyperclip beautifulsoup4 html-table-parser-python3 pandas alive_progress`

`pip install https://github.com/baseflow1/flint/archive/master.zip -U`

or navigate to the `requirements.txt` file and do `pip install -r requirements.txt`

## Usage
1. `git clone` this repo into a directory of your choosing
2. Change the `[path_to_disco]` string in `databaseGen.bat` to the path to your Discovery installation. (Remember to re-do this step everytime a patch hits.)
3. Run `databaseGen.bat` and enter the version of Disco that is used (for example 4.95.0)
4. Now run `pageGen.bat` in the same directory.

#### pageGen Usage
1. Enter the short name of your desired ship (i.e the one that is displayed in FLStat)
2. Copy-paste the image name from the page you intend to update. If you're creating a new page from scratch, you can also enter just `nickname`. This will use the internal nickname of the ship as the image name.
3. If the script can't figure it out itself, you will be prompted to enter the owner faction of your ship. This fills the `Built by` row in a ship's wiki-table, use what you find most appropriate here.
4. You're done! The page source has been copied into your clipboard and is ready to be pasted into the wiki itself. You will also be asked if you'd like the generate another page, enter `yes` if yes and just press Enter if no.
![pageGen.bat in use](/images/pageGen.png?raw=true "pageGen.bat in use")

---
Developed and tested on Python 3.10.4
