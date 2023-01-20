import requests
from json import load
from os.path import exists, isdir, split
from os import scandir
import time
from alive_progress import alive_bar
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument(
    "-n", "--nuke", help="Nuke all generated pages on the wiki", action="store_true"
)
argparser.add_argument("--systems", help="Update system pages", action="store_true")
argparser.add_argument("--ships", help="Update ship pages", action="store_true")
argparser.add_argument("-b", "--bases", help="Update base pages", action="store_true")
argparser.add_argument("-f", "--factions", help="Update faction pages", action="store_true")
argparser.add_argument("-i", "--images", help="Upload images", action="store_true")
argparser.add_argument("-c", "--commodities", help="Update commodities", action="store_true")
argparser.add_argument("-w", "--weapons", help="Update weapons", action="store_true")
argparser.add_argument("--special", help="Update Special Pages", action="store_true")
argparser.add_argument("-a", "--all", help="Update all Pages + Upload Images", action="store_true")
argparser.add_argument("-r", "--redirects", help="Update Redirects", action="store_true")
args = argparser.parse_args()

with open("config.json", "r") as f:
    config = load(f)

URL = config["bot"]["URL"]
delay = config["bot"]["delay"]


def login(botPasswordPath):
    if exists(botPasswordPath):
        with open(botPasswordPath, "r") as f:
            data = load(f)
            botName, botPassword = data["botCredentials"][0], data["botCredentials"][1]

        session = requests.Session()

        loginToken_params = {
            "action": "query",
            "format": "json",
            "meta": "tokens",
            "type": "login",
        }

        request = session.get(url=URL, params=loginToken_params)
        data = request.json()
        loginToken = data["query"]["tokens"]["logintoken"]

        login_params = {
            "action": "login",
            "lgname": botName,
            "lgpassword": botPassword,
            "lgtoken": loginToken,
            "format": "json",
        }
        request = session.post(URL, data=login_params)

        csrf_params = {"action": "query", "meta": "tokens", "format": "json"}

        request = session.get(url=URL, params=csrf_params)
        data = request.json()
        csrfToken = data["query"]["tokens"]["csrftoken"]

        return session, csrfToken


def regenerateTokens():
    global session
    global csrfToken
    session, csrfToken = login(config["bot"]["botPassword"])

def uploadText(session, csrfToken, wikitext, titleText):
    doLater = []
    doLater2 = []
    with alive_bar(len(wikitext.keys()), dual_line=True, title=titleText) as bar:
        for name, text in wikitext.items():
            bar.text = f"-> Updating: {name}"
            edit_params = {
                "action": "edit",
                "title": name,
                "text": text,
                "bot": True,
                "format": "json",
                "token": csrfToken,
            }
            request = session.post(URL, data=edit_params)
            data = request.json()
            try:
                error = data["error"]["code"]
                doLater.append([name, text])
                print(f"Error updating {name}: {error}, trying again later...")
                if error == "badtoken":
                    regenerateTokens()
            except:
                pass
            time.sleep(delay)
            bar()
    while True:
        if doLater != []:
            print("Retrying failed edits...")
            with alive_bar(len(doLater), dual_line=True, title=titleText) as bar:
                for name, text in doLater:
                    bar.text = f"-> Updating: {name}"
                    edit_params = {
                        "action": "edit",
                        "title": name,
                        "text": text,
                        "bot": True,
                        "format": "json",
                        "token": csrfToken,
                    }
                    request = session.post(URL, data=edit_params)
                    data = request.json()
                    try:
                        error = data["error"]["code"]
                        doLater2.append([name, text])
                        print(f"Error updating {name}: {error}, trying again later...")
                        if error == "badtoken":
                            regenerateTokens()
                    except:
                        doLater.remove([name, text])
                    time.sleep(delay * 2)
                    bar()
        else:
            break
        if doLater2 != []:
            doLater = doLater2
        doLater2 = []


def uploadImages(session, csrfToken, titleImage, path="../dumpedData/images"):
    subdirectories = []
    if exists(path):
        with scandir(path) as dirs:
            for entry in dirs:
                if isdir(entry.path):
                    subdirectories.append(entry.path)

    allimages_params = {
        "action": "query",
        "format": "json",
        "list": "allimages",
        "aiprop": "comment",
        "ailimit": 5000,
    }
    allimages = session.post(URL, data=allimages_params)
    allimages = allimages.json()["query"]["allimages"]
    allimages = {dic["name"].lower(): dic["comment"] for dic in allimages}

    doLater = []
    doLater2 = []
    for directory in subdirectories:
        with alive_bar(
            len([x for x in scandir(directory)]), dual_line=True, title=titleImage
        ) as bar:
            for entry in scandir(directory):
                if entry.name.endswith("png"):
                    try:
                        if allimages[entry.name] != config["bot"]["comment"]:
                            print(
                                f"Skipping {entry.name}, probably shouldn't be replaced."
                            )
                            bar()
                            continue
                    except:
                        pass
                    bar.text = (
                        f"-> Uploading: {entry.name} from folder {split(directory)[-1]}"
                    )
                    upload_params = {
                        "action": "upload",
                        "filename": entry.name,
                        "comment": config["bot"]["comment"],
                        "format": "json",
                        "token": csrfToken,
                        "bot": True,
                        "ignorewarnings": 1,
                    }
                    with open(entry.path, "rb") as fileParam:
                        file = {"file": (entry.name, fileParam, "multipart/form-data")}
                        request = session.post(URL, files=file, data=upload_params)
                    data = request.json()

                    try:
                        error = data["error"]["code"]
                        if not error == "fileexists-no-change":
                            print(
                                f"Error uploading {entry.name}: {error}, trying again later..."
                            )
                            doLater.append(entry)
                        else:
                            print(
                                f"File {entry.name} already exists on the wiki. {error}"
                            )
                    except:
                        pass
                    # time.sleep(delay)
                    bar()

    while True:
        if doLater != []:
            print("Retrying failed uploads...")
            with alive_bar(len(doLater), dual_line=True, title=titleImage) as bar:
                for entry in doLater:
                    if entry.name.endswith("png"):
                        bar.text = f"-> Uploading: {entry.name}"
                        upload_params = {
                            "action": "upload",
                            "filename": entry.name,
                            "comment": config["bot"]["comment"],
                            "format": "json",
                            "bot": True,
                            "token": csrfToken,
                            "ignorewarnings": 1,
                        }
                        with open(entry.path, "rb") as fileParam:
                            file = {
                                "file": (entry.name, fileParam, "multipart/form-data")
                            }
                            request = session.post(URL, files=file, data=upload_params)
                        data = request.json()
                        try:
                            error = data["error"]["code"]
                            if not error == "fileexists-no-change":
                                print(
                                    f"Error uploading {entry.name}: {error}, trying again later..."
                                )
                                doLater2.append(entry)
                            else:
                                print(
                                    f"File {entry.name} already exists on the wiki. {error}"
                                )
                        except:
                            pass
                        # time.sleep(delay * 2.5)
                        bar()
        else:
            break
        if doLater2 != []:
            doLater = doLater2
        doLater2 = []


def nukeTheWiki(session, csrfToken, titleNuke):
    queryNuke_params = {
        "action": "query",
        "generator": "categorymembers",
        "gcmtitle": config["bot"]["nukeCategory"],
        "prop": "categories",
        "bot": True,
        "cllimit": "max",
        "gcmlimit": "max",
        "format": "json",
    }

    request = session.post(URL, data=queryNuke_params)
    idsToNuke = list(request.json()["query"]["pages"].keys())

    with alive_bar(len(idsToNuke), dual_line=True, title=titleNuke) as bar:
        for id in idsToNuke:
            bar.text = f"Nuking pageID {id}"
            nuke_params = {
                "action": "delete",
                "format": "json",
                "reason": "This page has been nuked!",
                "pageid": id,
                "token": csrfToken,
            }

            request = session.post(URL, nuke_params)
            # print(request.json())

            # time.sleep(delay) seemingly not neccessary
            bar()


def main(wikidata = None, choices = None):      
    loginData = login(config["bot"]["botPassword"])

    if not wikidata:
        with open(config["bot"]["wikitext"], "r") as f:
            wikidata = load(f)

    wikitext = {}
    if args.systems or args.all or "systems" in choices:
        wikitext = wikitext | wikidata["Systems"]
    if args.ships or args.all or "ships" in choices:
        wikitext = wikitext | wikidata["Ships"]
    if args.bases or args.all or "bases" in choices:
        wikitext = wikitext | wikidata["Bases"]
    if args.factions or args.all or "factions" in choices:
        wikitext = wikitext | wikidata["Factions"]
    if args.commodities or args.all or "commodities" in choices:
        wikitext = wikitext | wikidata["Commodities"]
    if args.weapons or args.all or "weapons" in choices:
        wikitext = wikitext | wikidata["Weapons"]
    if args.redirects or args.all or "redirects" in choices:
        wikitext = wikitext | wikidata["Redirects"]
    if args.special or args.all or "special" in choices:
        wikitext = wikitext | wikidata["Special"]

    if args.nuke or "nuke" in choices:
        nukeTheWiki(
            session=loginData[0],
            csrfToken=loginData[1],
            titleNuke=config["bot"]["titleNuke"],
        )

    uploadText(
        session=loginData[0],
        csrfToken=loginData[1],
        wikitext=wikitext,
        titleText=config["bot"]["titleText"],
    )
    if args.images or args.all or "images" in choices:
        uploadImages(
            session=loginData[0],
            csrfToken=loginData[1],
            titleImage=config["bot"]["titleImage"],
            path=config["bot"]["images"],
        )


if __name__ == "__main__":
    main()
