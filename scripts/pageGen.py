import json
from os import getcwd
from os.path import exists

def loadData(filename):
    with open(f"{getcwd()}\\{filename}", "r") as file:
        data = json.load(file)
    return data

def main(template, data, config, nickname):
    houses = config["pageGen"]["houses"]
    corps = config["pageGen"]["corporations"]
    if template.lower() == "ship":
        ship_entry = data["Ships"][nickname]
        name = data["Ships"][nickname]["name"]
        infobox = '__NOTOC__\n<table class="infobox bordered" style=" margin-left: 1em; margin-bottom: 10px; width: 250px; font-size: 11px; line-height: 14px; border: 1px solid #555555;" cellpadding="3">\n\n<tr title={nickname}>\n<td colspan="2" style="text-align: center; font-size: 12px; line-height: 18px; background: #555555; color: #ffffff"><b>{name}</b>\n</td></tr>\n<tr>\n<td colspan="2" style="text-align: center; border: 1px solid #555555;"><div class="center"><div class="floatnone">[[File:{image}|center|250px]]</div></div>\n</td></tr>\n<tr>\n<td class="infobox-data-title"><b>Ship Class</b>\n</td>\n<td style="padding-right: 1em;">{class}\n</td>\n<tr>\n<td class="infobox-data-title"><b>Built by</b>\n</td>\n<td style="padding-right: 1em;">{built_by}\n</td>\n<tr>\n<td class="infobox-data-title"><b>[http://discoverygc.com/techcompat/techcompat_table.php Tech Column]</b>\n</td>\n<td style="padding-right: 1em;">{techcompat}\n</td>\n\n<tr>\n<td colspan="2" style="text-align: center; font-size: 14px; line-height: 18px; background: #555555; color: #ffffff">Technical Information\n</td></tr>\n<tr title="Amount of gun and turret hardpoints on this ship">\n<td class="infobox-data-title"><b>Guns/Turrets</b>\n</td>\n<td style="padding-right: 1em; font-weight: bold; letter-spacing: 1px;">{gunCount} / {turretCount}\n</td></tr>\n<tr title="Maximum class of weapons that can be mounted on this ship">\n<td class="infobox-data-title"><b>Max. weapon class</b>\n</td>\n<td style="padding-right: 1em;">{maxwep}\n</td></tr>\n<tr>\n<td class="infobox-data-title"><b>Other equipment</b>\n</td>\n<td style="padding-right: 1em;">\n<ul>\n{other}\n</ul></td></tr>\n<tr title="Amount of hull hitpoints">\n<td class="infobox-data-title"><b>Hull strength</b>\n</td>\n<td style="padding-right: 1em; color: #009900; font-weight: bold;">{hull}\n</td></tr>\n<tr title="Maximum class of shield that can be mounted on this ship">\n<td class="infobox-data-title"><b>Max. shield class</b>\n</td>\n<td style="padding-right: 1em; color: #006699; font-weight: bold;">{maxShield}\n</td></tr>\n<tr title="Amount of cargo this ship is able to carry">\n<td class="infobox-data-title"><b>Cargo space</b>\n</td>\n<td style="padding-right: 1em;">{cargo} units\n</td></tr>\n<tr title="Maximum number of shield batteries carried by this ship">\n<td class="infobox-data-title"><b>Batteries</b>\n</td>\n<td style="padding-right: 1em;">{batteries}\n</td></tr>\n<tr title="Maximum number of shield nanobots carried by this ship">\n<td class="infobox-data-title"><b>Nanobots</b>\n</td>\n<td style="padding-right: 1em;">{bots}\n</td></tr>\n<tr title="Maximum speed of this ship on impulse drive">\n<td class="infobox-data-title"><b>Max. impulse speed</b>\n</td>\n<td style="padding-right: 1em;">{impulse} m/s\n</td></tr>\n<tr title="Maximum turning speed in degrees per second">\n<td class="infobox-data-title"><b>Max. turn speed</b>\n</td>\n<td style="padding-right: 1em;">{turnRate} deg/s\n</td></tr>\n<tr title="Maximum speed of this ship on thrusters">\n<td class="infobox-data-title"><b>Max. thrust speed</b>\n</td>\n<td style="padding-right: 1em;">{maxthrust} m/s\n</td></tr>\n<tr title="Maximum speed of this ship on cruise engines">\n<td class="infobox-data-title"><b>Max. cruise speed</b>\n</td>\n<td style="padding-right: 1em;">{maxCruise} m/s\n</td></tr>\n<tr title="Maximum reactor energy storage (capacitance)">\n<td class="infobox-data-title"><b>Power output</b>\n</td>\n<td style="padding-right: 1em;">{power_output} u\n</td></tr>\n<tr title="Amount of energy units generated per second">\n<td class="infobox-data-title"><b>Power recharge</b>\n</td>\n<td style="padding-right: 1em;">{power_recharge} u/s\n</td></tr>\n<tr>\n<td colspan="2" style="text-align: center; font-size: 14px; line-height: 18px; background: #555555; color: #ffffff">Additional Information\n</td></tr>\n<tr title="Price of the ship without any mounted equipment">\n<td class="infobox-data-title"><b>Ship price</b>\n</td>\n<td style="padding-right: 1em;">${hull_price}\n</td></tr>\n<tr title="Price of the ship with the default equipment">\n<td class="infobox-data-title"><b>Package price</b>\n</td>\n<td style="padding-right: 1em;">${package_price}\n</td></tr></table>\n'
        infocard = '<p>{infocard}\n</p><p><br/>\n</p>\n'
        handling = '<h2>Handling</h2>\n<ul>\n{handling}\n</ul>\n'
        hardpoints = '<h2>Hardpoints</h2>\n<ul>\n{hardpoints}\n</ul>\n'
        includes = '<h2>Purchase Includes</h2>\n<ul>\n{includes}\n</ul>'
        availability = '<h2>Availability</h2>\n<table class="wikitable collapsible collapsed">\n<tr>\n<th>Buying Locations\n</th></tr>\n<tr>\n<td>\n<table class="wikitable sortable">\n<tr>\n<th>Base</th>\n<th>Owner</th>\n<th>System</th>\n<th>Location\n</th></tr>\n{sold_at}\n</td></tr></table>\n</td></tr></table>\n'
        time = '<i>NOTE: {time}<i>'
        category = '\n[[Category: Ships]]\n[[Category: nukeOnPatch]]\n{rest}'


        image = f'{nickname}.png'
    
        
        infobox = infobox.replace("{nickname}", nickname)
        infobox = infobox.replace("{name}", ship_entry["longName"])
        infobox = infobox.replace("{image}", image)
        infobox = infobox.replace("{class}", ship_entry["type"])
        if ship_entry["built_by"] != "":
            if ship_entry["built_by"] in houses:
                infobox = infobox.replace("{built_by}", f'[[File:Flag-{ship_entry["built_by"].lower()}.png|19px]] {ship_entry["built_by"]}')
            else:
                infobox = infobox.replace("{built_by}", f'{ship_entry["built_by"]}')
        else:
            infobox = infobox.replace("{built_by}", "Unknown")

        infobox = infobox.replace("{techcompat}", ship_entry["techcompat"])
        infobox = infobox.replace("{gunCount}", str(ship_entry["gunCount"]))
        infobox = infobox.replace("{turretCount}", str(ship_entry["turretCount"]))
        other = ""
        if ship_entry["torpedoCount"] > 0:
            other = f'{other}<li>{ship_entry["torpedoCount"]}xCD/T</li>\n'
        if ship_entry["cmCount"] > 0:
            other = f'{other}<li>{ship_entry["cmCount"]}xCM</li>\n'
        if ship_entry["mineCount"] > 0:
            other = f'{other}<li>{ship_entry["mineCount"]}xM</li>\n'
        infobox = infobox.replace("{other}", other)
        if ship_entry["maxThrust"] > 0:
            infobox = infobox.replace("{maxthrust}", str(ship_entry["maxThrust"]))
        else:
            infobox = infobox.replace("{maxthrust} m/s", '<span style="color: #f7001d; font-style: italic;">Thruster not available</span>')
        infobox = infobox.replace("{hull}", "{:,}".format(ship_entry["hit_pts"]))
        infobox = infobox.replace("{cargo}", "{:,}".format(ship_entry["hold_size"]))
        infobox = infobox.replace("{batteries}", "{:,}".format(ship_entry["bat_limit"]))
        infobox = infobox.replace("{bots}", "{:,}".format(ship_entry["bot_limit"]))
        infobox = infobox.replace("{maxwep}", str(ship_entry["maxClass"]))
        infobox = infobox.replace("{maxShield}", "{:,}".format(ship_entry["maxShield"]))
        infobox = infobox.replace("{impulse}", "{:,}".format(ship_entry["impulse_speed"]))
        infobox = infobox.replace("{turnRate}", "{:,}".format(ship_entry["turnRate"]))
        infobox = infobox.replace("{power_output}", "{:,}".format(ship_entry["power_output"]))
        infobox = infobox.replace("{maxCruise}", "{:,}".format(ship_entry["maxCruise"]))
        infobox = infobox.replace("{power_recharge}", "{:,}".format(ship_entry["power_recharge"]))
        infobox = infobox.replace("{hull_price}", "{:,}".format(ship_entry["hull_price"]))
        infobox = infobox.replace("{package_price}", "{:,}".format(ship_entry["package_price"]))

        info = ship_entry["infocard"].split("\n", 1)[1]
        while True:
            if info[0].isspace():
                info = info[1:len(info)]
            else:
                break
        infocard = infocard.replace("{infocard}", info)

        handleList = ship_entry["maneuverability"].split("\n")
        handle = ""
        if ship_entry["mustUseMoors"] == True:
            handle = "<li>This ship is too large to use docking bays, it must use mooring points.</li>\n"
        for entry in handleList:
            if entry != "":
                handle = f"{handle}<li>{entry}</li>\n"
        handling = handling.replace("{handling}", handle)

        harderpoint = ""
        for hardpoint in ship_entry["hardpoints"]:
            title = hardpoint.split(":")[0]
            count = hardpoint.split(":")[1]
            harderpoint = f"{harderpoint}<li>{count}x {title}</li>\n"
        hardpoints = hardpoints.replace("{hardpoints}", harderpoint)

        included = ""
        for title, price in ship_entry["equipment"]:
            included = f'{included}<li>{title} (${"{:,}".format(price)})</li>\n'
        includes = includes.replace("{includes}", included)

        sold_at = ""
        for base, owner, system, region in ship_entry["sold_at"]:
            region = "Independent Worlds" if region == "Independent" else region
            sold_at = f"{sold_at}<tr><td>[[{base}]]</td>\n<td>[[{owner}]]</td>\n<td>[[{system}]]</td>\n<td>{region}</td></tr>\n"
        availability = availability.replace("{sold_at}", sold_at)

        time = time.replace("{time}", ship_entry["time"])

        rest = ""
        if ship_entry["built_by"] != "":
            rest = rest +  f'[[Category: {ship_entry["built_by"]}]]\n'
        rest = rest +  f'[[Category: {ship_entry["type"]}]]'
        rest = rest +  f'[[Category: {ship_entry["techcompat"]}]]'

        category = category.replace("{rest}", rest)

        return f"{infobox}{infocard}{handling}{hardpoints}{includes}{availability}{time}{category}"
    elif "sys" in template.lower():
        entry = data["Systems"][nickname]
        name = data["Systems"][nickname]["name"]
        infobox = '__NOTOC__\n<table class="infobox bordered" style=" margin-left: 1em; margin-bottom: 10px; width: 250px; font-size: 11px; line-height: 14px; border: 1px solid #555555;" cellpadding="3">\n\n<td colspan="2" style="text-align: center; font-size: 12px; line-height: 18px; background: #555555; color: #ffffff"><b>{name}</b>\n</td></tr>\n<tr>\n<td colspan="2" style="text-align: center; border: 1px solid #555555;"><div class="center"><div class="floatnone">[[File:{image}|center|250px]]</div></div>\n</td></tr>\n\n<tr>\n<td colspan="2" style="text-align: center; font-size: 14px; line-height: 18px; background: #555555; color: #ffffff">System\n</td></tr>\n<tr>\n<td class="infobox-data-title"><b>Governing House</b>\n</td>\n<td style="padding-right: 1em">{governingHouse}\n</td></tr>\n\n<tr>\n<td class="infobox-data-title"><b>Region</b>\n</td>\n<td style="padding-right: 1em">{region}\n</td></tr>\n\n<tr>\n<td class="infobox-data-title"><b>Connected Systems</b>\n</td>\n<td style="padding-right: 1em">{systems}\n</td></tr>\n\n</td></tr></table>'
        infocard = '<p>{infocard}</p>\n<br style="clear: both; height: 0px;" />\n</p>\n'
        overview = '<h1><span class="mw-headline" id="System_Overview">System Overview</span></h1>\n<hr>\n<table style="width: 100%;">\n<tr>\n<td style="width: 33%; vertical-align: top; border-right: 1px dotted #999999; padding: .5em 1em; margin: 1em;">\n<div style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 150%; text-align: center; line-height: 1.5em; border-bottom-width: 1px; border-bottom-color: #AAAAAA; border-bottom-style: solid;">Astronomical Bodies</div>\n<div style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 133%; text-decoration: underline; line-height: 1.5em; padding-top: .5em;">Stellar Objects</div>\n{suns}\n<div style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 133%; text-decoration: underline; line-height: 1.5em; padding-top: .5em;">Planetary Objects</div>\n{planets}\n<div style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 133%; text-decoration: underline; line-height: 1.5em; padding-top: .5em;">Nebulae &amp; Asteroids</div>\n{fields}\n</td>\n<td style="width: 33%; vertical-align: top; border-right: 1px dotted #999999; padding: .5em 1em; margin: 1em;">\n<div style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 150%; text-align: center; line-height: 1.5em; border-bottom-width: 1px; border-bottom-color: #AAAAAA; border-bottom-style: solid;">Industrial Development</div>\n<div style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 133%; text-decoration: underline; line-height: 1.5em; padding-top: .5em;">Space Stations</div>\n{stations}\n<li class="mw-empty-elt"></li></ul>\n<div style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 133%; text-decoration: underline; line-height: 1.5em; padding-top: .5em;">Commodity Mining</div>\n{mining}\n</td>\n<td style="width: 33%; vertical-align: top; padding: .5em 1em; margin: 1em;">\n<div style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 150%; text-align: center; line-height: 1.5em; border-bottom-width: 1px; border-bottom-color: #AAAAAA; border-bottom-style: solid;">Faction Presence</div>\n<div style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 133%; text-decoration: underline; line-height: 1.5em; padding-top: .5em;">Lawful Factions</div>\n{lawfuls}\n<div style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 133%; text-decoration: underline; line-height: 1.5em; padding-top: .5em;">Corporations &amp; Guilds</div>\n{corps}\n<div style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 133%; text-decoration: underline; line-height: 1.5em; padding-top: .5em;">Unlawful Factions</div>\n{unlawfuls}\n</td></tr></table>\n'
        navmap = '<p><br style="clear: both; height: 0px;" />\n</p>\n<h1><span class="mw-headline" id="System_Map">System Map</span></h1>\n<hr>\n<p>[https://space.discoverygc.com/navmap/#q={name} Navmap]\n</p>\n'
        AoI = "<h1>Areas of Interest</h1>\n<hr>\n"
        nebulae = "<h2>Nebulae</h2>\n\n{nebulae}\n"
        asteroids = "<h2>Asteroid Fields</h2>\n\n{asteroids}\n"
        gates = '<h1>Jump Gates/Holes</h1>\n<hr>\n<table class="wikitable collapsible collapsed">\n<tr>\n<th>Jump Hole/Gate Locations \n</th></tr>\n<tr>\n<td>\n<table class="wikitable sortable">\n<tr>\n<th>Target System</th>\n<th>Type</th>\n<th>Sector</th></tr>\n{gates}\n</td></tr></table>\n</td></tr></table>\n'
        time = '<i>NOTE: {time}<i>'
        category = '\n[[Category: Systems]]\n[[Category: nukeOnPatch]]\n{region}'

        infobox = infobox.replace("{name}", entry["name"])
        infobox = infobox.replace("{image}", f'{nickname}.png')
        
        region = entry["region"]
        if region == "Independent": region = "Independent Worlds"
        if region in houses: 
            infobox = infobox.replace("{governingHouse}", f'[[File:Flag-{region.lower()}.png|19px]] {region}')
        else:
            infobox = infobox.replace("{governingHouse}", 'Independent')
        infobox = infobox.replace("{region}", region)
        temp = ""        
        for neighbor in entry["neighbors"]:
            temp = f"{temp}[[{neighbor}]]<br/>"
        infobox = infobox.replace("{systems}", temp)

        if exists(f'../infocards/systems/{nickname}.txt'):
            with open(f'../infocards/systems/{nickname}.txt', 'r') as f:
                info = f.read()
            infocard = infocard.replace("{infocard}", info.replace("\n", "<p>"))
        else:
            infocard = infocard.replace("{infocard}", "<i>No description available.</i>")
        
        temp = ""
        for star, card in entry["stars"].items():
            temp = f"{temp}<b>{star}</b><ul>"
            card = card[:-1]
            card = card.split("\n")
            for x in card: temp = f'{temp}<li>{x}</li>\n'
            temp = f"{temp}</ul>"
        overview = overview.replace("{suns}", temp)

        planets = '<table class="wikitable sortable">\n<tr>\n<th>Planet</th>\n<th>Owner</th>\n</tr>\n'
        edited = False
        for planet, nickname, owner in entry["planets"]:
            inhabited = f"{owner}" if owner != "" else "Uninhabited"
            planets = f"{planets}<tr><td><b>[[{planet}]]</b></td> <td>{inhabited}</td></tr>\n\n"
            edited = True
        if not edited:  planets = ""
        else:       planets = f"{planets}</table>"
        overview = overview.replace("{planets}", planets)

        
        temp = ""
        temp2 = []
        nebs = []
        asts = []
        for zone, nick, info in entry["zones"]:
            if zone in temp2: continue
            temp2.append(zone)
            temp = f"{temp}{zone}\n" if nick in [field[0] for field in entry["asteroids"]] or nick in [nebula[0] for nebula in entry["nebulae"]] else temp
            if nick in [nebula[0] for nebula in entry["nebulae"]]: nebs.append([zone, nick, info])
            elif nick in [field[0] for field in entry["asteroids"]]: asts.append([zone, nick, info])
        temp = temp[:-1].split("\n")
        temp.sort()
        temp3 = ""
        for x in temp: temp3 = f'{temp3}<li>{x}</li>\n'
        temp3 = "<ul>\n" +  temp3 + "</ul>\n"
        overview = overview.replace("{fields}", temp3)

        temp = ""
        bases = []
        lawfulFactions = []
        unlawfulFactions = []
        corporateFactions = []
        for base, dicty in entry["bases"].items():
            if dicty["type"] != "<class 'flint.entities.solars.PlanetaryBase'>":
                bases.append([base, dicty["owner"]])
            if dicty["owner"] in corps:
                corporateFactions.append(dicty["owner"])
            elif dicty["factionLegality"] == "Lawful":
                lawfulFactions.append(dicty["owner"])
            elif dicty["factionLegality"] == "Unlawful":
                unlawfulFactions.append(dicty["owner"])

        stations = '<table class="wikitable sortable">\n<tr>\n<th>Station</th>\n<th>Owner</th>\n</tr>\n'
        edited = False
        for base, owner in bases:
            stations = f"{stations}<tr><td><b>[[{base}]]</b></td> <td>{owner}</td></tr>\n"
            edited = True
        if not edited:  stations = ""
        else:       stations = f"{stations}</table>"
        overview = overview.replace("{stations}", stations)

        mineableCommodities = "<ul>"
        mineableCommodity = []
        for doesnt, matter, commodity in entry["asteroids"]:
            if commodity != None:
                mineableCommodity.append(commodity)
        mineableCommodity = list(dict.fromkeys(mineableCommodity))
        mineableCommodity.sort()
        for commodity in mineableCommodity:
            mineableCommodities = f"{mineableCommodities}<li>{commodity}</li>\n"
        overview = overview.replace("{mining}", mineableCommodities)

        lawfulFactions = list(dict.fromkeys(lawfulFactions))
        corporateFactions = list(dict.fromkeys(corporateFactions))
        unlawfulFactions = list(dict.fromkeys(unlawfulFactions))
        lawfulFactions.sort()
        corporateFactions.sort()
        unlawfulFactions.sort()
        lawfuls = "<ul>"
        corporates = "<ul>"
        unlawfuls = "<ul>"
        for faction in lawfulFactions:
            lawfuls = f"{lawfuls}<li>{faction}</li>\n"
        for faction in corporateFactions:
            corporates = f"{corporates}<li>{faction}</li>\n"
        for faction in unlawfulFactions:
            unlawfuls = f"{unlawfuls}<li>{faction}</li>\n"
        lawfuls = lawfuls + "</ul>"
        corporates = corporates + "</ul>"
        unlawfuls = unlawfuls + "</ul>"
        overview = overview.replace("{lawfuls}", lawfuls)
        overview = overview.replace("{corps}", corporates)
        overview = overview.replace("{unlawfuls}", unlawfuls)

        navmap = navmap.replace("{name}", name.replace(" ", "%20"))

        nebulas = ""
        asteroiden = ""
        for nebula, nick, card in nebs:
            nebulas = f"{nebulas}<h3>{nebula}</h3>\n{card}"
        for asteroid, nick, card in asts:
            asteroiden = f"{asteroiden}<h3>{asteroid}</h3>\n{card}"
        nebulae = nebulae.replace("{nebulae}", nebulas.replace("&nbsp;", ""))
        asteroids = asteroids.replace("{asteroids}", asteroiden.replace("&nbsp;", ""))

        jumps = ""
        for target, type, location in entry["holes"]:
            jumps = f"{jumps}<tr><td>[[{target}]]</td>\n<td>{type}</td>\n<td>{location}</td></tr>\n"
        gates = gates.replace("{gates}", jumps)

        time = time.replace("{time}", entry["time"])

        if region != "":
            category = category.replace("{region}", f'[[Category: {region}]]')
        else:
            category = category.replace("{region}", '')

        return f"{infobox}{infocard}{overview}{navmap}{AoI}{nebulae}{asteroids}{gates}{time}{category}"
    elif "base" in template.lower():
        entry = data["Bases"][nickname]
        name = entry["name"]        
        
        infobox = '__NOTOC__\n<table class="infobox bordered" style="float: right; margin-left: 1em; margin-bottom: 10px; width: 250px; font-size: 11px; line-height: 14px; border: 1px solid #555555;" cellpadding="3">\n\n<tr>\n<td colspan="2" style="text-align: center; font-size: 16px; line-height: 18px; background: #555555; color: #ffffff", title="{nickname}"><b>{name}</b>\n</td>\n</tr>\n<tr>\n<td colspan="2" style="text-align: center; border: 1px solid #555555;">\n<div class="center">\n<div class="floatnone">[[File:{nickname}.png|250px]]</div>\n</div>\n</td>\n</tr>\n<tr>\n<td colspan="2" style="text-align: center; font-size: 14px; line-height: 18px; background: #555555; color: #ffffff">Owner\n</td>\n</tr>\n<tr>\n<td colspan="2" style="text-align: center; font-size: 12px; line-height: 18px;">{owner}\n</td>\n</tr>\n<tr>\n<td colspan="2" style="text-align: center; font-size: 14px; line-height: 18px; background: #555555; color: #ffffff">Location\n</td>\n</tr>\n<tr>\n<td colspan="2" style="text-align: center; font-size: 12px; line-height: 18px;">{location}\n</td>\n</tr>\n</table>\n'
        infocard = '{infocard}\n'
        bribesNmissions = '<h2>Bribes & Missions Offered</h2>\n\n<table style="float: left; margin-bottom: 10px; margin-left: 1em; width: 25%; border: 1px solid #555555;" cellpadding="3">\n<tr>\n<td style="text-align: center; font-size: larger; background: #555555; color: #ffffff;"><b>Bribes</b>\n</td>\n</tr>\n<tr>\n<td style="padding-bottom: 7px;">\n{bribes}\n</td>\n</tr>\n</table>\n\n<table style="float: left; margin-bottom: 10px; margin-left: 1em; width: 25%; border: 1px solid #555555;" cellpadding="3">\n<tr>\n<td style="text-align: center; font-size: larger; background: #555555; color: #ffffff;"><b>Missions</b>\n</td>\n</tr>\n<tr>\n<td style="padding-bottom: 7px;">\n{missions}\n</td>\n</tr>\n</table>\n<p><br style="clear: both; height: 0px;" />\n'
        commodities = '<h2>Commodities</h2>\n\n<table class="wikitable collapsible mw-collapsible mw-collapsed" style="float: left; margin-bottom: 10px; margin-left: 1em; width: 25%; border: 1px solid #47505a;" cellpadding="3">\n<tr>\n<td style="text-align: center; font-size: larger; background: #555555; color: #ffffff;"><b>Imports</b>\n</td>\n</tr>\n<tr>\n<td style="padding-bottom: 7px;">\n{imports}\n</td>\n</tr>\n</table>\n<table class="wikitable collapsible mw-collapsible mw-collapsed" style="float: left; margin-bottom: 10px; margin-left: 1em; width: 25%; border: 1px solid #555555;" cellpadding="3">\n<tr>\n<td style="text-align: center; font-size: larger; background: #555555; color: #ffffff;"><b>Exports</b>\n</td>\n</tr>\n<tr>\n<td style="padding-bottom: 7px;">\n{exports}\n</td>\n</tr>\n</table>\n<p><br style="clear: both; height: 0px;" />\n'
        ships = '<h2>Ships sold</h2>\n\n\n<table class="wikitable sortable">\n<tr>\n<th>Ship</th>\n<th>Class</th>\n<th>Price</th>\n</tr>\n{ships_sold}\n</td></tr></table>\n<p><br style="clear: both; height: 0px;" />\n</p>\n'
        rumors = '<h2>Rumors</h2>\n{rumors}\n'
        time = '<i>NOTE: {time}<i>'
        categories = "\n[[Category: Bases]]\n[[Category: nukeOnPatch]]\n{other}"


        infobox = infobox.replace("{nickname}", nickname)
        infobox = infobox.replace("{name}", name)
        infobox = infobox.replace("{owner}", f'[[{entry["owner"]}]]')  
        infobox = infobox.replace("{location}", f"<b>{entry['sector']}</b>, [[{entry['system']}]]")


        info = entry["specs"] + "</font></font></b></i>" + "<p >" + entry["infocard"]
        infocard = infocard.replace("{infocard}", '<p style="padding: 0px; margin: 0px;">' + info.replace('<p>', '<p style="padding: 0px; margin: 0px;">'))


        bribes = "<ul>\n"
        for faction in entry["bribes"]: bribes = f"{bribes}<li>{faction}</li>\n"
        bribes = f"{bribes}</ul>"

        missions = "<ul>\n"
        for faction in entry["missions"]: missions = f"{missions}<li>{faction}</li>\n"
        missions = f"{missions}</ul>"

        bribesNmissions = bribesNmissions.replace("{bribes}", bribes)
        bribesNmissions = bribesNmissions.replace("{missions}", missions)

        imports = "<ul>\n"
        exports = "<ul>\n"

        for commodity in entry["commodities_buying"]:
            imports = f"{imports}<li>{commodity}</li>\n"
                
        for commodity in entry["commodities_selling"]:
            exports = f"{exports}<li>{commodity}</li>\n"
        
        imports = f"{imports}</ul>\n"
        exports = f"{exports}</ul>\n"

        commodities = commodities.replace("{imports}", imports)
        commodities = commodities.replace("{exports}", exports)

        shippos = ""
        for ship, type, price in entry["ships_sold"]:
            temp = "<tr>\n"
            temp = f'{temp}<td>[[{ship}]]</td>\n<td>{type}</td>\n<td>{"{:,}".format(price)}$</td>\n'
            temp = f"{temp}</tr>\n"
            shippos = f"{shippos}{temp}"

        ships = ships.replace("{ships_sold}", shippos)


        rumorTemplate = '<table style="margin-bottom: 10px; margin-left: 1em; width:90%; border: 1px solid #555555;" cellpadding="3">\n<tr>\n<td style="text-align: center; font-size: larger; background: #555555; color: #ffffff;"><b>[[{rumorFaction}]]</b>\n</td>\n</tr>\n<tr>\n<td style="padding-bottom: 7px;">\n{rumors}\n</td>\n</tr>\n</table>\n'
        rum = ""
        for faction, rumorList in entry["rumors"].items():
            temp = "<ul>"
            for rumor in rumorList:
                temp = f"{temp}<li>{rumor.replace('&nbsp;', '')}</li>\n"
            temp = f"{temp}</ul>"
            rum = f'{rum}{rumorTemplate.replace("{rumors}", temp).replace("{rumorFaction}", faction)}'
        
        rumors = rumors.replace("{rumors}", rum)

        time = time.replace("{time}", entry["time"])

        other = f'[[Category: {entry["owner"]}]]\n[[Category: {entry["region"]}]]\n[[Category: {entry["system"]}]]\n'
        categories = categories.replace("{other}", other)

        return f"{infobox}{infocard}{bribesNmissions}{commodities}{ships}{rumors}{time}{categories}"
    elif "faction" in template.lower():
        entry = data["Factions"][nickname]
        
        infobox = '__NOTOC__\n<table class="infobox bordered" style=" margin-left: 1em; margin-bottom: 10px; width: 250px; font-size: 11px; line-height: 14px; border: 1px solid #555555;" cellpadding="3">\n\n<td colspan="2" style="text-align: center; font-size: 12px; line-height: 18px; background: #555555; color: #ffffff", title = "{nickname}"><b>{name}</b>\n</td></tr>\n<tr>\n<td colspan="2" style="text-align: center; border: 1px solid #555555;"><div class="center"><div class="floatnone">[[File:{nickname}.png|center|250px]]</div></div>\n</td></tr>\n\n<tr>\n<td class="infobox-data-title"><b>Alignment</b>\n</td>\n<td style="padding-right: 1em">{alignment}\n</td></tr>\n</table>\n'
        infocard = '{infocard}\n'
        ships = '<h2 title="The ships this faction\'s NPC\'s use, as defined in faction_prop.ini">Ships used</h2>\n\n<table class="wikitable sortable">\n<tr>\n<th>Ship</th>\n<th>Class</th>\n</tr>\n{ships}\n</td></tr></table>\n'
        bases = '<h2 title="All bases that are owned by this faction">Bases owned</h2>\n\n<table class="wikitable collapsible mw-collapsible mw-collapsed">\n<tr>\n<th>\n</th>\n</tr>\n<tr>\n<td>\n<table class="wikitable sortable">\n<tr>\n<th>Base</th>\n<th>Owner</th>\n<th>System</th>\n<th>Region</th>\n</tr>\n{bases}\n</td></tr></table>\n</td></tr></table>\n'
        bribes = '<h2 title="All bases that offer bribes for this faction">Bribes</h2>\n\n<table class="wikitable collapsible mw-collapsible mw-collapsed">\n<tr>\n<th>\n</th>\n</tr>\n<tr>\n<td>\n<table class="wikitable sortable">\n<tr>\n<th>Base</th>\n<th>Owner</th>\n<th>System</th>\n<th>Region</th>\n</tr>\n{bribes}\n</td></tr></table>\n</td></tr></table>\n'
        rep_sheet = '<h2 title="This faction\'s rep sheet">Diplomacy</h2>\n\n<table class="wikitable collapsible mw-collapsible mw-collapsed">\n<tr>\n<th>\n</th></tr>\n<tr>\n<td>\n{{Faction Diplomacy/begin}}\n{repsheet}\n{{Faction Diplomacy/end}}\n</td></tr></table>'
        rumors = '<h2>Rumors</h2>\n<table class="wikitable collapsible mw-collapsible mw-collapsed">\n<tr>\n<th>\n</th>\n</tr>\n<tr>\n<td>\n{rumors}\n</td></tr></table>\n'
        time = '<i>NOTE: {time}<i>'
        categories = "\n[[Category: Factions]]\n[[Category: nukeOnPatch]]\n"


        infobox = infobox.replace("{nickname}", nickname)
        infobox = infobox.replace("{name}", entry["name"])
        infobox = infobox.replace("{alignment}", entry["alignment"])


        infocard = infocard.replace("{infocard}", entry["infocard"])

        shippos = ""
        for ship, type in entry["ships"]:
            shippos = f"{shippos}<tr>\n<td>[[{ship}]]</td>\n<td>{type}</td>\n</tr>\n"

        ships = ships.replace("{ships}", shippos)
        

        boses = ""
        for base, owner, system, region in entry["bases"]:
            boses = f"{boses}<tr>\n<td>[[{base}]]</td>\n<td>[[{owner}]]</td>\n<td>[[{system}]]</td>\n<td>{region}</td>\n</tr>\n"

        bases = bases.replace("{bases}", boses)

        brobes = ""
        for base, owner, system, region in entry["bribes"]:
            brobes = f"{brobes}<tr>\n<td>[[{base}]]</td>\n<td>[[{owner}]]</td>\n<td>[[{system}]]</td>\n<td>{region}</td>\n</tr>\n"

        bribes = bribes.replace("{bribes}", brobes)


        repsheet = ""
        for faction, rep in entry["repsheet"].items():
            rep = f"+{rep}" if rep > 0 else rep
            repsheet = f"{repsheet}((FD | [[{faction}]] | {rep}))\n".replace("((", "{{").replace("))", "}}")

        rep_sheet = rep_sheet.replace("{repsheet}", repsheet[:-1])

        rum = ""
        rumorTemplate = '<table style="margin-bottom: 10px; margin-left: 1em; width:90%; border: 1px solid #555555;" cellpadding="3">\n<tr>\n<td style="text-align: center; font-size: larger; background: #555555; color: #ffffff;"><b>[[{rumorBase}]]</b>\n</td>\n</tr>\n<tr>\n<td style="padding-bottom: 7px;">\n{rumors}\n</td>\n</tr>\n</table>\n'
        for base, rumorList in entry["rumors"].items():
            temp = "<ul>"
            for rumor in rumorList:
                temp = f"{temp}<li>{rumor.replace('&nbsp;', '')}</li>\n"
            temp = f"{temp}</ul>"
            rum = f'{rum}{rumorTemplate.replace("{rumors}", temp).replace("{rumorBase}", base)}'

        rumors = rumors.replace("{rumors}", rum)

        time = time.replace("{time}", entry["time"])

        return f"{infobox}{infocard}{ships}{bases}{bribes}{rep_sheet}{rumors}{time}{categories}"
    elif "commodity" in template.lower():
        entry = data["Commodities"][nickname]

        infobox = '__NOTOC__\n<table class="infobox bordered" style=" margin-left: 1em; margin-bottom: 10px; width: 250px; font-size: 11px; line-height: 14px; border: 1px solid #555555;" cellpadding="3">\n\n<td colspan="2" style="text-align: center; font-size: 12px; line-height: 18px; background: #555555; color: #ffffff" title="{nickname}"><b>{name}</b>\n</td></tr>\n<tr>\n<td colspan="2" style="text-align: center; border: 1px solid #555555;"><div class="center"><div class="floatnone">[[File:{nickname}.png|center|250px]]</div></div>\n</td></tr>\n\n<tr>\n<td class="infobox-data-title" title="The number of units of cargo this commodity uses"><b>Cargo Space</b>\n</td>\n<td style="padding-right: 1em">{volume}\n</td></tr>\n<tr>\n<td class="infobox-data-title" title="The rate at which this commodity decays per second"><b>Decay Rate</b>\n</td>\n<td style="padding-right: 1em">{decay}\n</td></tr>\n<tr>\n<td class="infobox-data-title"><b>Default Price</b>\n</td>\n<td style="padding-right: 1em">{price}\n</td></tr>\n</table>\n'
        infocard = '{infocard}\n'
        availability = '<h2>Availability</h2>\n\n<table class="wikitable collapsible mw-collapsible mw-collapsed" style="margin-bottom: 10px; margin-left: 1em; border: 1px solid #47505a;" cellpadding="3">\n<tr>\n<td style="text-align: center; font-size: larger; background: #555555; color: #ffffff;"><b>Buy locations</b>\n</td>\n</tr>\n<tr>\n<td style="padding-bottom: 7px;">\n<table class="wikitable sortable">\n<tr>\n<th>Base</th>\n<th>Owner</th>\n<th>System</th>\n<th>Region</th>\n<th>Price</th>\n</tr>\n{buyBases}\n</td></tr></table>\n\n</td>\n</tr>\n</table>\n<table class="wikitable collapsible mw-collapsible mw-collapsed" style="margin-bottom: 10px; margin-left: 1em; border: 1px solid #555555;" cellpadding="3">\n<tr>\n<td style="text-align: center; font-size: larger; background: #555555; color: #ffffff;"><b>Sell locations</b>\n</td>\n</tr>\n<tr>\n<td style="padding-bottom: 7px;">\n<table class="wikitable sortable">\n<tr>\n<th>Base</th>\n<th>Owner</th>\n<th>System</th>\n<th>Region</th>\n<th>Price</th>\n</tr>\n{sellBases}\n</td></tr></table>\n</td>\n</tr>\n</table>\n<p><br style="clear: both; height: 0px;" />\n<br style="clear: both; height: 0px;" />\n'
        time = '<i>NOTE: {time}<i>'
        categories = '[[Category: Commodities]]\n[[Category: nukeOnPatch]]\n'

        infobox = infobox.replace("{nickname}", nickname)
        infobox = infobox.replace("{name}", entry["name"])
        infobox = infobox.replace("{volume}", str(entry["volume"]))
        infobox = infobox.replace("{decay}", str(entry["decay"]) if entry["decay"] else "<i>no decay</i>")
        infobox = infobox.replace("{price}", '{:,}'.format(entry["defaultPrice"]) + '$')


        infocard = infocard.replace("{infocard}", entry["infocard"].replace("&nbsp;", ""))

        boughtAt = ""
        soldAt = ""
        for base in entry["boughtAt"]:
            name, owner, system, region, price = base[0], base[1], base[2], base[3], base[4]
            boughtAt = f"{boughtAt}<tr>\n<td>[[{name}]]</td>\n<td>[[{owner}]]</td>\n<td>[[{system}]]</td>\n<td>{region}</td>\n<td>{'{:,}'.format(price)}$</td>\n</tr>\n"
        for base in entry["soldAt"]:
            name, owner, system, region, price = base[0], base[1], base[2], base[3], base[4]
            soldAt = f"{soldAt}<tr>\n<td>[[{name}]]</td>\n<td>[[{owner}]]</td>\n<td>[[{system}]]</td>\n<td>{region}</td>\n<td>{'{:,}'.format(price)}$</td>\n</tr>\n"

        availability = availability.replace("{buyBases}", boughtAt)
        availability = availability.replace("{sellBases}", soldAt)

        time = time.replace("{time}", entry["time"])

        return f"{infobox}{infocard}{availability}{time}{categories}"

loadedData = loadData("../dumpedData/flData.json")
configData = loadData("config.json")
sources = {}

sysSource = {}
print("Processing Systems")
for name, attributes in loadedData["Systems"].items():
    source = main(template = "System", data = loadedData, config = configData, nickname = name)
    sysSource[attributes["name"]] = source
sources["Systems"] = sysSource

shipSource = {}
print("Processing Ships")
for name, attributes in loadedData["Ships"].items():
    source = main(template = "Ship", data = loadedData, config = configData, nickname = name)        
    shipSource[attributes["name"]] = source
sources["Ships"] = shipSource

baseSource = {}
print("Processing Bases")
for name, attributes in loadedData["Bases"].items():
    source = main(template = "Base", data = loadedData, config = configData, nickname = name)
    name = attributes["name"] if attributes["name"] not in sources["Ships"].keys() else f'{attributes["name"]} (b)'
    baseSource[name] = source
sources["Bases"] = baseSource

factionSource = {}
print("Processing Factions")
for name, attributes in loadedData["Factions"].items():
    source = main(template = "Faction", data = loadedData, config = configData, nickname = name)        
    factionSource[attributes["name"]] = source
sources["Factions"] = factionSource

commoditySource = {}
print("Processing Commodities")
for name, attributes in loadedData["Commodities"].items():
    source = main(template = "Commodity", data = loadedData, config = configData, nickname = name)        
    commoditySource[attributes["name"]] = source
sources["Commodities"] = commoditySource
print("DONE")

with open("../dumpedData/wikitext.json", "w") as f:
    json.dump(sources, f, indent=1)