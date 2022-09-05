import requests
from json import load
from os.path import exists
import time
from alive_progress import alive_bar

URL = "https://disco-freelancer.fandom.com/api.php"
delay = 1


if exists("botPassword.json") and exists("wikitext.json"):
    with open("botPassword.json", "r") as f:
        data = load(f)
        botName, botPassword = data[0], data[1]
    with open("wikitext.json", "r") as f:
        wikitext = load(f)
    
    headerData = {
        'Content-Type': 'multipart/form-data'
    }

    session = requests.Session()

    loginToken_params = {
        "action": "query",
        "format": "json",
        "meta": "tokens",
        "type": "login"
    }

    request = session.get(url=URL, params=loginToken_params)
    data = request.json()
    #print(data)
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
    #print(data)
    csrfToken = data['query']['tokens']['csrftoken']

    doLater = []
    with alive_bar(len(wikitext.keys()), dual_line=True, title="mediawikiBot.py") as bar:
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
            #print(data)
            try:
                error = data['error']["code"]
                doLater.append([name, text])
                print(f"Error uploading {name}: {error}, trying again later...")
            except:
                pass
            time.sleep(delay)
            bar()
    if doLater != []:
        print("Retrying failed uploads...")
        with alive_bar(len(doLater), dual_line=True, title="mediawikiBot.py") as bar:
            for name, text in doLater:
                bar.text = f'-> Uploading: {name}: {error}'
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
                #print(data)
                try:
                    data['error']
                    doLater.append([name, text])
                    print(f"Error uploading {name}.")
                except:
                    pass
                time.sleep(delay * 2.5)
                bar()