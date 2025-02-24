import pageGen
import json
import os
from flint.paths import is_probably_freelancer
import requests
from bs4 import BeautifulSoup
import subprocess

try:
    import flWikiGen
    import mediawikiBot
except FileNotFoundError:
    pass


def clearConsole():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def firstTimeSetup():
    while True:
        print("""Input the Path to your Freelancer installation:""")
        freelancerPath = input()
        if is_probably_freelancer(freelancerPath):
            clearConsole()
            break
        else:
            print("Path is not a valid Freelancer installation, trying again...")

    print(
        """Input the API-Link to your Wiki (default: "https://disco-freelancer.fandom.com/api.php"):"""
    )
    wikiLink = input("")
    wikiLink = (
        "https://disco-freelancer.fandom.com/api.php" if not wikiLink else wikiLink
    )

    clearConsole()
    print(
        f"""Input your Bot Username and Password
    If you don't have one, navigate to /wiki/Special:BotPasswords to create one.
    More info: https://www.mediawiki.org/wiki/Manual:Bot_passwords"""
    )
    botP1 = input("Wiki-Account-Username: ")
    botP2 = input("Bot-Name: ")
    botP3 = input("Bot-Password: ")
    botCredentials = [f"{botP1}@{botP2}", botP3]

    clearConsole()
    while True:
        print("""Input the path to the root of a Librelancer install""")
        librelancer = input("Path: ")
        if os.path.exists(librelancer + "/lleditscript.exe"):
            break
        else:
            print("Path does not contain lleditscript.exe. Try again")

    while True:
        print("""Input the path to the root of a Blender install""")
        blender = input("Path: ")
        if os.path.exists(blender + "/blender.exe"):
            break
        else:
            print("Path does not contain blender.exe. Try again")        

    with open("./secret.json", "w") as f:
        json.dump(
            {
                "freelancerPath": freelancerPath,
                "URL": wikiLink,
                "botCredentials": botCredentials,
                "librelancer": librelancer,
                "blender": blender
            },
            f,
            indent=1,
        )

def ask(question: str):
    print(question)
    answer = True if "y" in input() else False
    clearConsole()
    return answer

def pagesToUpdate():
    nuke = ask("Nuke the wiki before updating? y/N")
    dumpModels = ask("Dump ship models for rendering? y/N")
    renderShips = ask("Render ships in Blender? y/N\nWARNING: This might take a while!")
    print(
        """Which of the following (if any) pages do you wish to update?
    (a) Systems
    (b) Ships
    (c) Bases
    (d) Factions
    (e) Commodities
    (f) Weapons
    (g) Countermeasures
    (h) Armor
    (i) Cloaks
    (j) Engines
    (k) Shields
    (1) Redirects
    (2) Special
    (3) Images
    (x) All of the above
    """
    )
    print("")
    selection = input()
    options = {
        "systems": True if "a" in selection or "x" in selection else False,
        "ships": True if "b" in selection or "x" in selection else False,
        "bases": True if "c" in selection or "x" in selection else False,
        "factions": True if "d" in selection or "x" in selection else False,
        "commodities": True if "e" in selection or "x" in selection else False,
        "weapons": True if "f" in selection or "x" in selection else False,
        "cms": True if "g" in selection or "x" in selection else False,
        "armor": True if "h" in selection or "x" in selection else False,
        "cloaks": True if "i" in selection or "x" in selection else False,
        "engines": True if "j" in selection or "x" in selection else False,
        "shields": True if "k" in selection or "x" in selection else False,
        "redirects": True if "1" in selection or "x" in selection else False,
        "special": True if "2" in selection or "x" in selection else False,
        "images": True if "3" in selection or "x" in selection else False,
        "nuke": nuke,
        "dumpModels": dumpModels,
        "renderShips": renderShips,
    }
    clearConsole()
    return [option for option, chosen in options.items() if chosen == True]


def callBot():
    choices = pagesToUpdate()
    print(
        f"""You chose the following:
{choices}
Confirm? y/N
    """
    )
    if "dumpModels" in choices:
        clear_folder("../dumpedData/models/")
    if "renderShips" in choices:
        clear_folder("../dumpedData/images/ships/")

    if "y" in input():
        clearConsole()
        print("Dumping game data\n===================")
        flData = flWikiGen.main(dumpModels = "dumpModels" in choices)
        if "renderShips" in choices:
            blender_render()
        wikitext = pageGen.main(flData)
        clearConsole()
        if "dumpModels" in choices:
            choices.remove("dumpModels")
        if "renderShips" in choices:
            choices.remove("renderShips")
        mediawikiBot.main(wikidata=wikitext, choices=choices)
    else:
        quit()


def downloadServerConfig(url="https://discoverygc.com/gameconfigpublic/"):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.find_all("a")
    urls = {
        "https://discoverygc.com/gameconfigpublic/" + link.get("href") for link in links
    }

    for i, url in enumerate(urls):
        print(
            f"{i+1}/{len(urls)} Downloading {url.split('/')[-1]}.                    ",
            end="\r",
        )
        r = requests.get(url)
        if r.ok:
            with open(f"./server_config/{url.split('/')[-1]}", "wb") as f:
                f.write(r.content)

def clear_folder(folder: str):
    files = [os.path.abspath(folder + f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

    for file in files:
        os.remove(file)

def blender_render():
    blender = os.path.join(secret["blender"], "blender.exe")
    clearConsole()
    os.environ["PYTHONPATH"] = "../.venv/Lib/site-packages"
    subprocess.call([blender, os.path.abspath("./renderer.blend"), "-b", "-P", os.path.abspath("./blender.py")])
    input()

if __name__ == "__main__":
    with open("./config.json", "r") as f:
        config = json.load(f)
    if not os.path.exists("./secret.json"):
        print("Running first time setup...")
        firstTimeSetup()
        clearConsole()
        import flWikiGen
        import mediawikiBot

    with open("./secret.json", "r") as f:
        secret = json.load(f)
    downloadServerConfig()
    print("")
    callBot()
