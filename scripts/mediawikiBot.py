import time
from json import load
from os import scandir
from os.path import exists, isdir, split

import requests
from alive_progress import alive_bar

with open("config.json", "r") as f:
    config = load(f)

with open(config["bot"]["botPassword"], "r") as f:
    URL = load(f)["URL"]

delay = config["bot"]["delay"]


def login(bot_password_path):
    if not exists(bot_password_path):
        raise FileNotFoundError

    with open(bot_password_path, "r") as f:
        data = load(f)
        bot_name, bot_password = data["botCredentials"][0], data["botCredentials"][1]

    session = requests.Session()

    login_token_params = {
        "action": "query",
        "format": "json",
        "meta": "tokens",
        "type": "login",
    }

    request = session.get(url=URL, params=login_token_params)
    data = request.json()
    login_token = data["query"]["tokens"]["logintoken"]

    login_params = {
        "action": "login",
        "lgname": bot_name,
        "lgpassword": bot_password,
        "lgtoken": login_token,
        "format": "json",
    }
    request = session.post(URL, data=login_params)

    csrf_params = {"action": "query", "meta": "tokens", "format": "json"}

    request = session.get(url=URL, params=csrf_params)
    data = request.json()
    csrf_token = data["query"]["tokens"]["csrftoken"]

    return session, csrf_token


def upload_text(wikitext, title_text):
    def upload(to_upload):
        session, csrf_token = login(config["bot"]["botPassword"])
        failed_uploads = {}
        for name, text in to_upload.items():
            bar.text = f"-> Updating: {name}"
            edit_params = {
                "action": "edit",
                "title": name,
                "text": text,
                "bot": True,
                "format": "json",
                "token": csrf_token,
            }
            request = session.post(URL, data=edit_params)
            data = request.json()
            try:
                error = data["error"]["code"]
                if error == "ratelimited":
                    failed_uploads[name] = text
                print(f"Error updating {name}: {error}, trying again later...")
                if error == "badtoken":
                    session, csrf_token = login(config["bot"]["botPassword"])
            except:
                bar()
            time.sleep(delay)

        return failed_uploads

    with alive_bar(len(wikitext.keys()), dual_line=True, title=title_text) as bar:
        failures = upload(wikitext)

        while failures:
            failures = upload(failures)


def upload_images(title_image, path="../dumpedData/images"):
    def get_wiki_images():
        session, csrf_token = login(config["bot"]["botPassword"])
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
        session, csrf_token = login(config["bot"]["botPassword"])
        failed_uploads = []
        with alive_bar(len(entries), dual_line=True, title=title_image) as bar:
            for entry in entries:
                if not (entry["name"].endswith("png") or entry["name"].endswith("glb")):
                    continue

                try:
                    if allimages[entry["name"]] != config["bot"]["comment"]:
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
                    "filename": entry["name"],
                    "comment": config["bot"]["comment"],
                    "format": "json",
                    "token": csrf_token,
                    "bot": True,
                    "ignorewarnings": 1,
                }
                with open(entry["path"], "rb") as fileParam:
                    file = {"file": (entry["name"], fileParam, "multipart/form-data")}
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
                        failed_uploads.append(
                            {"name": entry["name"], "path": entry["path"]}
                        )
                except:
                    pass
                # time.sleep(delay)
                bar()
        return failed_uploads

    subdirectories = set()
    if exists(path):
        with scandir(path) as dirs:
            for entry in dirs:
                if isdir(entry.path):
                    subdirectories.add(entry.path)

    allimages = get_wiki_images()

    failures = []
    for directory in subdirectories:
        entries = [
            {"name": entry.name, "path": entry.path} for entry in scandir(directory)
        ]
        failures = failures + upload(entries)

    while failures:
        failures = upload(failures)


def nuke_the_wiki(title_nuke):
    session, csrf_token = login(config["bot"]["botPassword"])

    def nuke():
        session, csrf_token = login(config["bot"]["botPassword"])
        with alive_bar(len(ids_to_nuke), dual_line=True, title=title_nuke) as bar:
            for id in ids_to_nuke:
                bar.text = f"Nuking pageID {id}"
                nuke_params = {
                    "action": "delete",
                    "format": "json",
                    "reason": "This page has been nuked!",
                    "pageid": id,
                    "token": csrf_token,
                }

                request = session.post(URL, nuke_params)
                try:
                    error = request.json()["error"]["code"]
                    print(f"Error updating {id}: {error}, trying again later...")
                    if error == "badtoken":
                        session, csrf_token = login(config["bot"]["botPassword"])
                    bar()
                except:
                    bar()
                # print(request.json())

                # time.sleep(delay) # seemingly not neccessary

    query_nuke_params = {
        "action": "query",
        "generator": "categorymembers",
        "gcmtitle": config["bot"]["nukeCategory"],
        "prop": "categories",
        "bot": True,
        "cllimit": "max",
        "gcmlimit": "max",
        "format": "json",
    }

    request = session.post(URL, data=query_nuke_params)
    ids_to_nuke = set(request.json()["query"]["pages"].keys())

    nuke()


def add_warning():
    session, csrf_token = login(config["bot"]["botPassword"])
    edit_params = {
        "action": "edit",
        "title": "Main_Page",
        "prependtext": "{{Warning|text=The Wiki is currently being updated. Information may be out-of-date or missing.}}\n",
        "summary": "Adding update warning for the duration of the update.",
        "bot": True,
        "format": "json",
        "token": csrf_token,
    }
    request = session.post(URL, data=edit_params)
    data = request.json()

    return data.get("edit", {}).get("newrevid", 0)


def undo_edit(title, rev_id):
    session, csrf_token = login(config["bot"]["botPassword"])
    edit_params = {
        "action": "edit",
        "title": title,
        "undo": rev_id,
        "summary": f"Update complete, undoing revision {rev_id}",
        "bot": True,
        "format": "json",
        "token": csrf_token,
    }

    request = session.post(URL, data=edit_params)
    data = request.json()

    return bool(data.get("edit", {}).get("result") == "Success")


def main(wikidata=None, choices=None):
    if not wikidata:
        with open(config["bot"]["wikitext"], "r") as f:
            wikidata = load(f)

    if not choices:
        print("Exiting since nothing should be updated")
        return

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
    if "redirects" in choices:
        wikitext = wikitext | wikidata["Redirects"]
    if "special" in choices:
        wikitext = wikitext | wikidata["Special"]

    print("Adding update warning to Main_Page")
    global warningRevId
    warningRevId = add_warning()

    if "nuke" in choices:
        nuke_the_wiki(
            title_nuke=config["bot"]["titleNuke"],
        )

    upload_text(
        wikitext=wikitext,
        title_text=config["bot"]["titleText"],
    )
    if "images" in choices:
        upload_images(
            title_image=config["bot"]["titleImage"],
            path=config["bot"]["images"],
        )
    if "models" in choices:
        upload_images(
            title_image=config["bot"]["titleModels"],
            path=config["bot"]["models"],
        )

    if warningRevId:
        print("Removing update warning")
        undo_edit("Main_Page", warningRevId)


if __name__ == "__main__":
    global warningRevId
    main()
