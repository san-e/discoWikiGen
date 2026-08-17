import json
import os
import subprocess

import requests
from bs4 import BeautifulSoup
from flint.paths import is_probably_freelancer

import dump
import mediawikiBot
import pageGen

# Set working directory to scripts folder
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def clear_console():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def first_time_setup():
    while True:
        print("""Input the Path to your Freelancer installation:""")
        freelancerPath = input()
        if is_probably_freelancer(freelancerPath):
            clear_console()
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

    clear_console()
    print(f"""Input your Bot Username and Password
    If you don't have one, navigate to /wiki/Special:BotPasswords to create one.
    More info: https://www.mediawiki.org/wiki/Manual:Bot_passwords""")
    botP1 = input("Wiki-Account-Username: ")
    botP2 = input("Bot-Name: ")
    botP3 = input("Bot-Password: ")
    botCredentials = [f"{botP1}@{botP2}", botP3]

    clear_console()
    while True:
        print("""Input the path to the root of a Librelancer install""")
        librelancer = input("Path: ")
        if os.path.exists(
            librelancer + f"/lleditscript{'.exe' if os.name == 'nt' else ''}"
        ):
            break
        else:
            print(
                f"Path does not contain lleditscript{'.exe' if os.name == 'nt' else ' executable'}. Try again"
            )

    while True:
        print(
            """Input the path to a Firefox binary
        You will only need this if you intend to dump system maps from the online Navmap"""
        )
        firefox = input("Path: ")
        if os.path.exists(firefox) + os.path.isfile(firefox):
            break
        else:
            print(f"Path does not point to a Firefox binary. Try again")

    while True:
        print(
            """Input the path to a geckodriver binary (download here: https://github.com/mozilla/geckodriver/releases)
        You will only need this if you intend to dump system maps from the online Navmap"""
        )
        geckodriver = input("Path: ")
        if os.path.exists(firefox) + os.path.isfile(firefox):
            break
        else:
            print(f"Path does not point to a geckodriver binary. Try again")

    with open("./secret.json", "w") as f:
        json.dump(
            {
                "freelancerPath": freelancerPath,
                "URL": wikiLink,
                "botCredentials": botCredentials,
                "librelancer": librelancer,
                "firefox": firefox,
                "webdriver": geckodriver,
            },
            f,
            indent=1,
        )


def ask(question: str):
    print(question)
    answer = True if "y" in input() else False
    clear_console()
    return answer


def pages_to_update():
    nuke = ask("Nuke the wiki before updating? y/N")
    dump_models = ask("Dump Ship Models? y/N")
    render = ask("Render Ships? y/N")
    dump_sysmaps = ask("Dump System Maps? y/N")
    dump_icons = ask("Dump Good Icons? y/N")
    print("""Which of the following (if any) pages do you wish to update?
    (a) Systems
    (b) Ships
    (c) Bases
    (d) Factions
    (e) Commodities
    (f) Weapons
    (g) Solars
    (1) Redirects
    (2) Special
    (3) Images
    (4) Models
    (x) All of the above
    """)
    print("")
    selection = input()
    options = {
        "systems": True if "a" in selection or "x" in selection else False,
        "ships": True if "b" in selection or "x" in selection else False,
        "bases": True if "c" in selection or "x" in selection else False,
        "factions": True if "d" in selection or "x" in selection else False,
        "commodities": True if "e" in selection or "x" in selection else False,
        "weapons": True if "f" in selection or "x" in selection else False,
        "solars": True if "g" in selection or "x" in selection else False,
        "redirects": True if "1" in selection or "x" in selection else False,
        "special": True if "2" in selection or "x" in selection else False,
        "images": True if "3" in selection or "x" in selection else False,
        "models": True if "4" in selection or "x" in selection else False,
        "nuke": nuke,
        "dumpModels": dump_models,
        "renderShips": render,
        "dumpSysmaps": dump_sysmaps,
        "dumpIcons": dump_icons
    }
    clear_console()
    return [option for option, chosen in options.items() if chosen == True]


def call_bot():
    choices = pages_to_update()
    print(f"""You chose the following:
{choices}
Confirm? y/N
    """)

    if "y" in input():
        if "dumpModels" in choices:
            clear_folder("../dumpedData/models/")
            dump.dump(models=True)
        if "renderShips" in choices:
            clear_folder("../dumpedData/images/ships/")
            dump.dump(ship_render=True)
        if "dumpSysmaps" in choices:
            clear_folder("../dumpedData/images/systems/")
            dump.dump(sysmaps=True)
        if "dumpIcons" in choices:
            clear_folder("../dumpedData/images/news/")
            dump.dump(icons=True)
        clear_console()
        wikitext = pageGen.main()
        clear_console()
        if "dumpModels" in choices:
            choices.remove("dumpModels")
        if "renderShips" in choices:
            choices.remove("renderShips")
        if "dumpSysmaps" in choices:
            choices.remove("dumpSysmaps")
        mediawikiBot.main(wikidata=wikitext, choices=choices)
    else:
        quit()


def download_server_config(url="https://discoverygc.com/gameconfigpublic/"):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.find_all("a")
    urls = {url + link.get("href") for link in links}

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
    files = [
        os.path.abspath(folder + f)
        for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
    ]

    for file in files:
        os.remove(file)


def blender_render():
    blender = os.path.join(
        secret["blender"], f"blender{'.exe' if os.name == 'nt' else ''}"
    )
    clear_console()
    os.environ["PYTHONPATH"] = os.path.abspath("../.venv/Lib/site-packages")
    subprocess.call(
        [
            blender,
            os.path.abspath("./renderer.blend"),
            "-b",
            "-P",
            os.path.abspath("./blender.py"),
        ]
    )
    input()


if __name__ == "__main__":
    with open("./config.json", "r") as f:
        config = json.load(f)
    if not os.path.exists("./secret.json"):
        print("Running first time setup...")
        first_time_setup()
        clear_console()

    with open("./secret.json", "r") as f:
        secret = json.load(f)
    download_server_config()
    print("")
    call_bot()
