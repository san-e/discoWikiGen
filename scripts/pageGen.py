import json
from pyperclip import copy
from os import getcwd

def loadData(filename):
    with open(f"{getcwd()}\\{filename}", "r") as file:
        data = json.load(file)
    return data

classToWikiType = {
    "Light Fighter" : "L_FIGHTER",
    "Heavy Fighter" : "H_FIGHTER",
    "Very Heavy Fighter" : "VH_FIGHTER",
    "Super Heavy Fighter" : "SH_FIGHTER",
    "Bomber" : "BOMBER",
    "Gunship" : "GUNBOAT",
    "Gunboat" : "GUNBOAT",
    "Cruiser" : "CRUISER",
    "Battlecruiser" : "BATTLECRUISER",
    "Battleship" : "BATTLESHIP",
    "Dreadnought" : "DREADNOUGHT",
    "Carrier" : "CARRIER",
    "Freighter" : "FREIGHTER",
    "Liner" : "LINER",
    "Transport" : "TRANSPORT",
    "Destroyer" : "CRUISER",
    "Repair Ship" : "FREIGHTER",
    "Train" : "TRANSPORT",
    "Super Train" : "TRANSPORT",
    "Heavy Transport" : "TRANSPORT"
}



def main(template, data, config):
    if template.lower() == "ship":
        version = "{{Version|{version}}}\n"
        infobox = "{{Ship Infobox\n| name = {name}\n| image = {image}\n| nickname = {nickname}\n| shipclass = {class}\n| shipowner = {{House Link | {built_by}}}\n| shiptechcategory = {techcompat}\n| techmix = {techcompat}\n| guns = {gunCount}\n| turrets = {turretCount}\n| torpedoes = {torpedoCount}\n| mines = {mineCount}\n| CM = {cmCount}\n| hull = {hull}\n| cargo = {cargo}\n| maxregens = {regens}\n| optwepclass = {optwep}\n| maxwepclass = {maxwep}\n| maxshieldclass = {maxShield}\n| maxspeed = {impulse_speed}\n| maxturn = {turnRate}\n| maxthrust = {maxthrust}\n| maxpower = {power_output}\n| maxcruise = {maxCruise}\n| recharge = {power_recharge}\n| hullcost = {hull_price}\n| fullcost = {package_price}\n}}\n\n"
        infocard = "{infocard}\n\n"
        handling = "==Handling==\n{handling}\n"
        hardpoints = "==Hardpoints==\n{hardpoints}\n"
        includes = "==Purchase Includes==\n{{Spoiler|\n{includes}\n}}\n\n"
        availability = "==Availability==\n{| class=\"wikitable collapsible collapsed\"\n!Spoiler: Buying Locations\n|-\n|\n{| class=\"wikitable sortable\"\n|-\n!Base!!Owner!!System!!Location\n{sold_at}\n|}\n|}"
        category = "\n[[Category: {built_by}]]"
        while True:
            name = str(input("Enter ship name (as displayed in FLStat): "))
            try:
                if data["Ships"][name]:
                    break
            except:
                print("Ship name could not be found in database, retrying...")
        image = str(input("Enter image name (copy-paste from page source): "))
        if image == "":
            image = "li_fighter.png"
            print(f"No Image has been specified, defaulting to {image}")
        elif image.lower() == "nickname":
            image = f'{data["Ships"][name]["nickname"]}.png'
            print("Using Ship's nickname as image name.")

        version = version.replace("{version}", data["Version"])

        infobox = infobox.replace("{name}", data["Ships"][name]["longName"])
        infobox = infobox.replace("{image}", image)
        infobox = infobox.replace("{nickname}", data["Ships"][name]["nickname"])
        infobox = infobox.replace("{class}", classToWikiType[data["Ships"][name]["type"]])
        if data["Ships"][name]["built_by"] != "":
            infobox = infobox.replace("{built_by}", data["Ships"][name]["built_by"])
        else:
            built = str(input("Enter ship owner faction: "))
            infobox = infobox.replace("{{House Link | {built_by}}}", f"[[{built}]]")
        infobox = infobox.replace("{techcompat}", data["Ships"][name]["techcompat"])
        infobox = infobox.replace("{gunCount}", str(data["Ships"][name]["gunCount"]))
        infobox = infobox.replace("{turretCount}", str(data["Ships"][name]["turretCount"]))
        infobox = infobox.replace("{torpedoCount}", str(data["Ships"][name]["torpedoCount"])) if data["Ships"][name]["torpedoCount"] != 0 else infobox.replace("{torpedoCount}", "")
        infobox = infobox.replace("{mineCount}", str(data["Ships"][name]["mineCount"])) if data["Ships"][name]["mineCount"] != 0 else infobox.replace("{mineCount}", "")
        infobox = infobox.replace("{cmCount}", str(data["Ships"][name]["cmCount"])) if data["Ships"][name]["cmCount"] != 0 else infobox.replace("{cmCount}", "")
        infobox = infobox.replace("{maxthrust}", str(data["Ships"][name]["maxThrust"]))
        infobox = infobox.replace("{hull}", str(data["Ships"][name]["hit_pts"]))
        infobox = infobox.replace("{cargo}", str(data["Ships"][name]["hold_size"]))
        infobox = infobox.replace("{regens}", str(data["Ships"][name]["bat_limit"]))
        infobox = infobox.replace("{optwep}", str(data["Ships"][name]["maxClass"]))
        infobox = infobox.replace("{maxwep}", str(data["Ships"][name]["maxClass"]))
        infobox = infobox.replace("{maxShield}", str(data["Ships"][name]["maxShield"]))
        infobox = infobox.replace("{impulse_speed}", str(data["Ships"][name]["impulse_speed"]))
        infobox = infobox.replace("{turnRate}", str(data["Ships"][name]["turnRate"]))
        infobox = infobox.replace("{power_output}", str(data["Ships"][name]["power_output"]))
        infobox = infobox.replace("{maxCruise}", str(data["Ships"][name]["maxCruise"]))
        infobox = infobox.replace("{power_recharge}", str(data["Ships"][name]["power_recharge"]))
        infobox = infobox.replace("{hull_price}", str(data["Ships"][name]["hull_price"]))
        infobox = infobox.replace("{package_price}", str(data["Ships"][name]["package_price"]))


        info = data["Ships"][name]["infocard"].split("\n", 1)[1]
        while True:
            if info[0].isspace():
                info = info[1:len(info)]
            else:
                break
        infocard = infocard.replace("{infocard}", info)

        handle = data["Ships"][name]["maneuverability"].replace("\n", "\n* ")
        if data["Ships"][name]["mustUseMoors"] == True:
            handle.replace('*', '**')
            handle = f"* This ship is too large to use docking bays, it must use mooring points.{handle}"
            handling = handling.replace("{handling}", handle)
        else:
            handling = handling.replace("{handling}", handle)


        hardpoint = ""
        for x in data["Ships"][name]["hardpoints"]:
            if "Cruiser Shield Upgrade" in x:
                x = x.replace("Cruiser Shield Upgrade", "Shield Harmonic Reinforcement")
            try:
                if "Gun" in x:
                    temp = x.split("(")[1]
                    temp = temp.split(")")[0]
                    temp = temp.replace(" ", "_")
                    temp2 = x.split("[[")[1]
                    temp2 = temp2.split("]]")[0]
                    #print(f"* [[{temp}_Guns|{temp2}]]")
                    x = x.replace(temp2, f"{temp}_Guns|{temp2}")
            except IndexError:
                pass
            hardpoint = hardpoint + x + "\n"
        hardpoints = hardpoints.replace("{hardpoints}", hardpoint)

        include = ""
        temp = ""
        for x in data["Ships"][name]["equipment"]:
            number = "{:,}".format(x[1])
            if "Shield" in x[0]:
                temp = x[0].split("[[")[1]
                temp = temp.split("]]")[0]
                x[0] = x[0].replace(temp, f"Shields|{temp}")
            elif "Armor" in x[0]:
                temp = x[0].split("[[")[1]
                temp = temp.split("]]")[0]
                x[0] = x[0].replace(temp, f"Armor_Upgrades|{temp}")
            include = f"{include}{x[0]} (${number})\n"
        includes = includes.replace("{includes}", include)

        available = ""
        for x in data["Ships"][name]["sold_at"]:
            if x[3] == "Independent":
                x[3] = "Independent Worlds"
            available = f"{available}|-\n|[[{x[0]}]]||[[{x[1]}]]||[[{x[2]}]]||[[{x[3]}]]\n"
        availability = availability.replace("{sold_at}", available)

        if data["Ships"][name]["built_by"] != "":
            category = category.replace("{built_by}", data["Ships"][name]["built_by"])
        else:
            category = ""
        if handle != "":
            return f"{version}{infobox}{infocard}{handling}{hardpoints}{includes}{availability}{category}"
        else:
            return f"{version}{infobox}{infocard}{hardpoints}{includes}{availability}{category}"
    elif "sys" in template.lower():    
        version = "{{Version|{version}}}\n"
        infobox = "{{System v2\n| name = {name}\n| nickname = {nickname}\n| image = {nickname}.png\n| government = {government}\n| region = {region}\n| neighbors = {neighbors}\n"
        description = "| description = {description}\n"
        overview = "| suns = {suns}\n| fields = {fields}\n| lawful-factions = {lawfuls}\n| trade-factions = {traders}\n| unlawful-factions = {unlawfuls}\n| stations = {bases}\n| planets = {planets}\n| mining-zones = {miningZones}\n}}\n"
        navmap = "=System Map=\n[https://space.discoverygc.com/navmap/#q={name} Navmap]\n"
        AoI = "=Areas of Interest=\n"
        nebulae = "==Nebulae==\n\n{nebulae}\n"
        asteroids = "==Asteroid Fields==\n\n{asteroids}\n"
        jumps = '==Jump Gates/Holes==\n{| class="wikitable collapsible collapsed"\n!Spoiler: Jump Hole/Gate Locations\n|-\n|\n|-\n|\n{| class="wikitable sortable"\n!Target System!!Location!!Type\n{gates}\n|}\n|}'
        category = "\n[[Category: {region}]]"

        while True:
            name = str(input("Enter system name: "))
            try:
                if data["Systems"][name]:
                    break
            except:
                print("System could not be found in database, retrying...")
        version = version.replace("{version}", data["Version"])

        infobox = infobox.replace("{name}", name)
        infobox = infobox.replace("{nickname}", data["Systems"][name]["nickname"])
        region = data["Systems"][name]["region"]
        if region == "Independent": region = "Independent Worlds"
        if region in config["settings"]["houses"]: 
            infobox = infobox.replace("{government}", "{{" + f'House Link|{region}' + "}}")
        else:
            infobox = infobox.replace("{government}", 'Independent')
        infobox = infobox.replace("{region}", region)
        temp = ""        
        for neighbor in data["Systems"][name]["neighbors"]:
            temp = f"{temp}[[{neighbor}]]<br/>"
        infobox = infobox.replace("{neighbors}", temp)

        description = description.replace("{description}", "")

        temp = ""
        for star, card in data["Systems"][name]["stars"].items():
            card = '\n' + card[:-1]
            card = card.replace("\n", "\n* ")
            temp = f"{temp}'''{star}'''\n{card}\n"
        overview = overview.replace("{suns}", temp)
        temp = ""
        temp2 = []
        nebs = []
        asts = []
        for zone, nick, info in data["Systems"][name]["zones"]:
            if zone in temp2: continue
            temp2.append(zone)
            temp = f"{temp}{zone}\n" if nick in [field[0] for field in data["Systems"][name]["asteroids"]] or nick in [nebula[0] for nebula in data["Systems"][name]["nebulae"]] else temp
            if nick in [nebula[0] for nebula in data["Systems"][name]["nebulae"]]: nebs.append([zone, nick, info])
            elif nick in [field[0] for field in data["Systems"][name]["asteroids"]]: asts.append([zone, nick, info])
        temp = "* " + temp.replace('\n', '\n* ')
        overview = overview.replace("{fields}", temp)
        temp = ""
        bases = []
        lawfulFactions = []
        unlawfulFactions = []
        corporateFactions = []
        for base, dicty in data["Systems"][name]["bases"].items():
            if dicty["type"] != "<class 'flint.entities.solars.PlanetaryBase'>":
                bases.append([base, dicty["owner"]])
            if dicty["owner"] in [x[0] for x in config["settings"]["corporations"]]:
                corporateFactions.append(dicty["owner"])
            elif dicty["factionLegality"] == "Lawful":
                lawfulFactions.append(dicty["owner"])
            elif dicty["factionLegality"] == "Unlawful":
                unlawfulFactions.append(dicty["owner"])
        lawfulFactions = list(dict.fromkeys(lawfulFactions))
        corporateFactions = list(dict.fromkeys(corporateFactions))
        unlawfulFactions = list(dict.fromkeys(unlawfulFactions))
        lawfulFactions.sort()
        corporateFactions.sort()
        unlawfulFactions.sort()
        lawfuls = "* "
        corporates = "* "
        unlawfuls = "* "
        for faction in lawfulFactions:
            lawfuls = f"{lawfuls}[[{faction}]]\n"
        for faction in corporateFactions:
            corporates = f"{corporates}[[{faction}]]\n"
        for faction in unlawfulFactions:
            unlawfuls = f"{unlawfuls}[[{faction}]]\n"
        lawfuls = lawfuls.replace("\n", "\n* ")
        corporates = corporates.replace("\n", "\n* ")
        unlawfuls = unlawfuls.replace("\n", "\n* ")
        overview = overview.replace("{lawfuls}", lawfuls)
        overview = overview.replace("{traders}", corporates)
        overview = overview.replace("{unlawfuls}", unlawfuls)
        stations = "* "
        for base, owner in bases:
            stations = f"{stations}'''[[{base}]]''' -- ''[[{owner}]]''\n"
        stations = stations.replace("\n", "\n* ")
        overview = overview.replace("{bases}", stations)
        planets = "\n"
        brrt = ""
        for planet, nickname, owner in data["Systems"][name]["planets"]:
            inhabited = "Inhabited" if owner != "" else "Uninhabited"
            planet = planet if planet != " " else "Unknown"
            if inhabited == "Inhabited":
                planets = f"{planets}§§Planet|{planet}|{inhabited} -- [[{owner}]]|{nickname}.png$$\n"
            else:
                planets = f"{planets}§§Planet|{planet}|{inhabited}|{nickname}.png$$\n"
            brrt = f"{brrt}<br/><br/>"
        planets = planets.replace("§", "{")
        planets = planets.replace("$", "}")
        planets = f"{planets}{brrt}"
        overview = overview.replace("{planets}", planets)
        mineableCommodities = ""
        mineableCommodity = []
        for doesnt, matter, commodity in data["Systems"][name]["asteroids"]:
            if commodity != None:
                mineableCommodity.append(commodity)
        mineableCommodity = list(dict.fromkeys(mineableCommodity))
        mineableCommodity.sort()
        for commodity in mineableCommodity:
            mineableCommodities = f"{mineableCommodities}* [[{commodity}]]\n"
        overview = overview.replace("{miningZones}", mineableCommodities)

        navmap = navmap.replace("{name}", name.replace(" ", "%20"))

        nebul = "\n"
        ast = "\n"
        for nebula, nick, info in nebs:
            nebul = f"{nebul}\n'''{nebula}'''\n\n<p>{info}\n"
        for field, nick, info in asts:
            ast = f"{ast}\n'''{field}'''\n\n<p>{info}\n"
        nebul = nebul.replace("<p></b>", "</b>")
        ast = ast.replace("<p></b>", "</b>")
        nebulae = nebulae.replace("{nebulae}", nebul)
        asteroids = asteroids.replace("{asteroids}", ast)

        gates = ""
        for system, type, sector in data["Systems"][name]["holes"]:
            gates = f"{gates}|-\n|[[{system}]]||{sector}||{type}\n"
        jumps = jumps.replace("{gates}", gates)

        category = category.replace("{region}", data["Systems"][name]["region"])





        return f"{version}{infobox}{description}{overview}{navmap}{AoI}{nebulae}{asteroids}{jumps}{category}"
    else:
        return False


loadedData = loadData("flData.json")
configData = loadData("config.json")
while True:
    templates = ["Ship", "System"]
    source = main(template = input(f"Select template ({templates}): "), data = loadedData, config = configData)
    if source != False:
        copy(source)
        print("Page source copied!")
    else:
        print("Page source could not be copied.")
    
    repeat = input("Generate another page? (yes/No): ")
    if repeat == "" or 'n' in repeat.lower(): break
    elif 'y' in repeat.lower(): pass