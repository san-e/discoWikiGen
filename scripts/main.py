import pageGen
import json
import os
from flint.paths import is_probably_freelancer
import requests
from bs4 import BeautifulSoup

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
        print("""Input the path to the root a Librelancer install""")
        librelancer = input("Path: ")
        if os.path.exists(librelancer + "/lleditscript.exe"):
            break
        else:
            print("Path does not look like a complete Librelancer install. Try again")

    with open("./secret.json", "w") as f:
        json.dump(
            {
                "freelancerPath": freelancerPath,
                "URL": wikiLink,
                "botCredentials": botCredentials,
                "librelancer": librelancer,
            },
            f,
            indent=1,
        )


def nukeWiki():
    print("Nuke the wiki before updating? y/N")
    nuke = True if "y" in input() else False
    clearConsole()
    return nuke


def pagesToUpdate():
    nuke = nukeWiki()
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
    if "y" in input():
        clearConsole()
        print("Dumping game data\n===================")
        flData = flWikiGen.main()
        wikitext = pageGen.main(flData)
        clearConsole()
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


if __name__ == "__main__":
    with open("./config.json", "r") as f:
        config = json.load(f)
    if not os.path.exists("./secret.json"):
        print("Running first time setup...")
        firstTimeSetup()
        clearConsole()
        import flWikiGen
        import mediawikiBot
    downloadServerConfig()
    print("")
    callBot()
