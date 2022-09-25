import requests
from json import load
from os.path import exists, isdir, split
from os import scandir
import time
from alive_progress import alive_bar

with open("config.json", "r") as f:
    config = load(f)

URL = config["bot"]["URL"]
delay = config["bot"]["delay"]


def login(botPasswordPath):
    if exists(botPasswordPath):
        with open(botPasswordPath, "r") as f:
            data = load(f)
            botName, botPassword = data[0], data[1]
        
        session = requests.Session()

        loginToken_params = {
            "action": "query",
            "format": "json",
            "meta": "tokens",
            "type": "login"
        }

        request = session.get(url=URL, params=loginToken_params)
        data = request.json()
        loginToken = data['query']['tokens']['logintoken']

        login_params = {
            "action": "login",
            "lgname": botName,
            "lgpassword": botPassword,
            "lgtoken": loginToken,
            "format": "json"
        }
        request = session.post(URL, data=login_params)

        csrf_params = {
            "action": "query",
            "meta": "tokens",
            "format": "json"
        }

        request = session.get(url=URL, params=csrf_params)
        data = request.json()
        csrfToken = data['query']['tokens']['csrftoken']

        return session, csrfToken

def uploadText(session, csrfToken, wikitextPath, titleText):
        if exists(wikitextPath):
            with open(wikitextPath, "r") as f:
                wikitext = load(f)
            doLater = []
            doLater2 = []
            with alive_bar(len(wikitext.keys()), dual_line=True, title=titleText) as bar:
                for name, text in wikitext.items():
                    bar.text = f'-> Uploading: {name}'
                    edit_params = {
                        "action": "edit",
                        "title": name,
                        "text": text,
                        "bot": True,
                        "format": "json",
                        "token": csrfToken
                    }
                    request = session.post(URL, data = edit_params)
                    data = request.json()
                    try:
                        error = data['error']["code"]
                        doLater.append([name, text])
                        print(f"Error uploading {name}: {error}, trying again later...")
                    except:
                        pass
                    time.sleep(delay)
                    bar()
            while True:
                if doLater != []:
                    print("Retrying failed uploads...")
                    with alive_bar(len(doLater), dual_line=True, title=titleText) as bar:
                        for name, text in doLater:
                            bar.text = f'-> Uploading: {name}'
                            edit_params = {
                                "action": "edit",
                                "title": name,
                                "text": text,
                                "bot": True,
                                "format": "json",
                                "token": csrfToken
                            }
                            request = session.post(URL, data = edit_params)
                            data = request.json()
                            try:
                                error = data['error']["code"]
                                doLater2.append([name, text])
                                print(f"Error uploading {name}: {error}, trying again later...")
                            except:
                                pass
                            time.sleep(delay * 2.5)
                            bar()
                else:
                    break
                if doLater2 != []: doLater = doLater2
                doLater2 = []

def uploadImages(session, csrfToken, titleImage, path = "../dumpedData/images"):
    subdirectories = []
    if exists(path):
        with scandir(path) as dirs:
            for entry in dirs:
                if isdir(entry.path):
                    subdirectories.append(entry.path)
    
    doLater = [] 
    doLater2 = []
    for directory in subdirectories:
        with alive_bar(len([x for x in scandir(directory)]), dual_line=True, title=titleImage) as bar:
            for entry in scandir(directory):
                if entry.name.split(".")[-1] == "png":
                    bar.text = f'-> Uploading: {entry.name} from folder {split(directory)[-1]}'
                    upload_params = {
                        "action": "upload",
                        "filename": entry.name,
                        "format": "json",
                        "token": csrfToken,
                        "ignorewarnings": 1
                        }
                    with open(entry.path, 'rb') as fileParam:
                        file = {'file':(entry.name, fileParam, 'multipart/form-data')}
                        request = session.post(URL, files=file, data=upload_params)
                    data = request.json()

                    try:
                        error = data['error']["code"]
                        if not error == "fileexists-no-change":
                            print(f"Error uploading {entry.name}: {error}, trying again later...")
                            doLater.append(entry)
                        else:
                            print(f"File {entry.name} already exists on the wiki. {error}")
                    except:
                        pass
                    #time.sleep(delay)
                    bar()

    while True:
        if doLater != []:
            print("Retrying failed uploads...")
            with alive_bar(len(doLater), dual_line=True, title=titleImage) as bar:
                for entry in doLater:
                    if entry.name.split(".")[-1] == "png":
                        bar.text = f'-> Uploading: {entry.name}'
                        upload_params = {
                            "action": "upload",
                            "filename": entry.name,
                            "format": "json",
                            "token": csrfToken,
                            "ignorewarnings": 1
                            }
                        with open(entry.path, 'rb') as fileParam:
                            file = {'file':(entry.name, fileParam, 'multipart/form-data')}
                            request = session.post(URL, files=file, data=upload_params)
                        data = request.json()
                        try:
                            error = data['error']["code"]
                            if not error == "fileexists-no-change":
                                print(f"Error uploading {entry.name}: {error}, trying again later...")
                                doLater2.append(entry)
                            else:
                                print(f"File {entry.name} already exists on the wiki. {error}")
                        except:
                            pass
                        #time.sleep(delay * 2.5)
                        bar()
        else:
            break
        if doLater2 != []: doLater = doLater2
        doLater2 = []


if __name__ == "__main__":
    loginData = login(config["bot"]["botPassword"])
    uploadText(
        session = loginData[0],
        csrfToken = loginData[1],
        wikitextPath = config["bot"]["wikitext"],
        titleText = config["bot"]["titleText"]
    )
    uploadImages(
        session = loginData[0],
        csrfToken = loginData[1],
        titleImage = config["bot"]["titleImage"],
        path = config["bot"]["images"]
    )    
