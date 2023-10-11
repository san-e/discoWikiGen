import requests
from json import load
from os.path import exists, isdir, split
from os import scandir
import time
from alive_progress import alive_bar
from pprint import pprint

with open("config.json", "r") as f:
    config = load(f)

with open(config["bot"]["botPassword"], "r") as f:
    URL = load(f)["URL"]

delay = config["bot"]["delay"]


def login(botPasswordPath):
    if not exists(botPasswordPath):
        raise FileNotFoundError

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

    csrf_params = {
        "action": "query",
        "meta": "tokens",
        "format": "json"
    }

    request = session.get(url=URL, params=csrf_params)
    data = request.json()
    csrfToken = data["query"]["tokens"]["csrftoken"]

    return session, csrfToken


def uploadText(wikitext, titleText):
    def upload(toUpload):
        session, csrfToken = login(config["bot"]["botPassword"])
        failedUploads = {}
        with alive_bar(len(toUpload.keys()), dual_line=True, title=titleText) as bar:
            for name, text in toUpload.items():
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
                    failedUploads[name] = text
                    print(f"Error updating {name}: {error}, trying again later...")
                    if error == "badtoken":
                        session, csrfToken = login(config["bot"]["botPassword"])
                    bar()
                except:
                    pass
                    bar()
                time.sleep(delay)
        
        return failedUploads

    failures = upload(wikitext)

    while failures:
        failures = upload(failures)


def uploadImages(titleImage, path="../dumpedData/images"):
    subdirectories = set()
    if exists(path):
        with scandir(path) as dirs:
            for entry in dirs:
                if isdir(entry.path):
                    subdirectories.add(entry.path)


    def getWikiImages():
        session, csrfToken = login(config["bot"]["botPassword"])
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
        return allimages

    def upload(entries):
        session, csrfToken = login(config["bot"]["botPassword"])
        failedUploads = []
        with alive_bar(len(entries), dual_line=True, title=titleImage) as bar:
            for entry in entries:
                if not entry["name"].endswith("png"):
                    continue

                try:
                    if allimages[entry['name']] != config["bot"]["comment"] and False:
                        print(
                            f"Skipping {entry['name']}, probably shouldn't be replaced."
                        )
                        bar()
                        continue
                except:
                    pass

                bar.text = (
                    f"-> Uploading: {entry['name']} from folder {split(directory)[-1]}"
                )
                upload_params = {
                    "action": "upload",
                    "filename": entry['name'],
                    "comment": config["bot"]["comment"],
                    "format": "json",
                    "token": csrfToken,
                    "bot": True,
                    "ignorewarnings": 1,
                }
                with open(entry['path'], "rb") as fileParam:
                    file = {"file": (entry['name'], fileParam, "multipart/form-data")}
                    request = session.post(URL, files=file, data=upload_params)
                data = request.json()

                try:
                    error = data["error"]["code"]
                    if error == "fileexists-no-change":
                        print(
                            f"File {entry['name']} already exists on the wiki. {error}"
                        )

                    else:
                        print(
                            f"Error uploading {entry['name']}: {error}, trying again later..."
                        )
                        failedUploads.append({"name": entry['name'], "path": entry['path']})
                except:
                    pass
                # time.sleep(delay)
                bar()
        return failedUploads
    
    allimages = getWikiImages()

    failures = []
    for directory in subdirectories:
        entries = [{"name": entry.name, "path": entry.path} for entry in scandir(directory)]
        failures = failures + upload(entries)

    while failures:
        failures = upload(failures)


def nukeTheWiki(titleNuke):
    session, csrfToken = login(config["bot"]["botPassword"])
    def nuke():
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

                # time.sleep(delay) # seemingly not neccessary
                bar()
                
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
    idsToNuke = set(request.json()["query"]["pages"].keys())

    nuke()



def main(wikidata = None, choices = None):      
    if not wikidata:
        with open(config["bot"]["wikitext"], "r") as f:
            wikidata = load(f)

    print(URL)

    wikitext = {}
    if "systems" in choices:
        wikitext = wikitext | wikidata["Systems"]
    if "ships" in choices:
        wikitext = wikitext | wikidata["Ships"]
    if "bases" in choices:
        wikitext = wikitext | wikidata["Bases"]
    if "factions" in choices:
        wikitext = wikitext | wikidata["Factions"]
    if "commodities" in choices:
        wikitext = wikitext | wikidata["Commodities"]
    if "weapons" in choices:
        wikitext = wikitext | wikidata["Weapons"]
    if "cms" in choices:
        wikitext = wikitext | wikidata["CMs"]
    if "armor" in choices:
        wikitext = wikitext | wikidata["Armor"]
    if "cloaks" in choices:
        wikitext = wikitext | wikidata["Cloaks"]
    if "engines" in choices:
        wikitext = wikitext | wikidata["Engines"]
    if "shields" in choices:
        wikitext = wikitext | wikidata["Shields"]
    if "redirects" in choices:
        wikitext = wikitext | wikidata["Redirects"]
    if "special" in choices:
        wikitext = wikitext | wikidata["Special"]

    if "nuke" in choices:
        nukeTheWiki(
            titleNuke=config["bot"]["titleNuke"],
        )

    uploadText(
        wikitext=wikitext,
        titleText=config["bot"]["titleText"],
    )
    if "images" in choices:
        uploadImages(
            titleImage=config["bot"]["titleImage"],
            path=config["bot"]["images"],
        )


if __name__ == "__main__":
    main()
