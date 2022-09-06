import json
from os import getcwd
from os.path import exists
import sys

def loadData(filename):
    with open(f"{getcwd()}\\{filename}", "r") as file:
        data = json.load(file)
    return data


def main(template, data, config, name):
    houses = config["settings"]["houses"]
    if template.lower() == "ship":
        infobox = '__NOTOC__\n<table class="infobox bordered" style=" margin-left: 1em; margin-bottom: 10px; width: 250px; font-size: 11px; line-height: 14px; border: 1px solid #555555;" cellpadding="3">\n\n<tr title={nickname}>\n<td colspan="2" style="text-align: center; font-size: 12px; line-height: 18px; background: #555555; color: #ffffff"><b>{name}</b>\n</td></tr>\n<tr>\n<td colspan="2" style="text-align: center; border: 1px solid #555555;"><div class="center"><div class="floatnone">[[File:{image}|center|250px]]</div></div>\n</td></tr>\n<tr>\n<td class="infobox-data-title"><b>Ship Class</b>\n</td>\n<td style="padding-right: 1em;">{class}\n</td>\n<tr>\n<td class="infobox-data-title"><b>Built by</b>\n</td>\n<td style="padding-right: 1em;">{built_by}\n</td>\n<tr>\n<td class="infobox-data-title"><b>[http://discoverygc.com/techcompat/techcompat_table.php Tech Column]</b>\n</td>\n<td style="padding-right: 1em;">{techcompat}\n</td>\n\n<tr>\n<td colspan="2" style="text-align: center; font-size: 14px; line-height: 18px; background: #555555; color: #ffffff">Technical Information\n</td></tr>\n<tr title="Amount of gun and turret hardpoints on this ship">\n<td class="infobox-data-title"><b>Guns/Turrets</b>\n</td>\n<td style="padding-right: 1em; font-weight: bold; letter-spacing: 1px;">{gunCount} / {turretCount}\n</td></tr>\n<tr title="Maximum class of weapons that can be mounted on this ship">\n<td class="infobox-data-title"><b>Max. weapon class</b>\n</td>\n<td style="padding-right: 1em;">{maxwep}\n</td></tr>\n<tr>\n<td class="infobox-data-title"><b>Other equipment</b>\n</td>\n<td style="padding-right: 1em;">\n<ul>\n{other}\n</ul></td></tr>\n<tr title="Amount of hull hitpoints">\n<td class="infobox-data-title"><b>Hull strength</b>\n</td>\n<td style="padding-right: 1em; color: #009900; font-weight: bold;">{hull}\n</td></tr>\n<tr title="Maximum class of shield that can be mounted on this ship">\n<td class="infobox-data-title"><b>Max. shield class</b>\n</td>\n<td style="padding-right: 1em; color: #006699; font-weight: bold;">{maxShield}\n</td></tr>\n<tr title="Amount of cargo this ship is able to carry">\n<td class="infobox-data-title"><b>Cargo space</b>\n</td>\n<td style="padding-right: 1em;">{cargo} units\n</td></tr>\n<tr title="Maximum number of shield batteries carried by this ship">\n<td class="infobox-data-title"><b>Batteries</b>\n</td>\n<td style="padding-right: 1em;">{batteries}\n</td></tr>\n<tr title="Maximum number of shield nanobots carried by this ship">\n<td class="infobox-data-title"><b>Nanobots</b>\n</td>\n<td style="padding-right: 1em;">{bots}\n</td></tr>\n<tr title="Maximum speed of this ship on impulse drive">\n<td class="infobox-data-title"><b>Max. impulse speed</b>\n</td>\n<td style="padding-right: 1em;">{impulse} m/s\n</td></tr>\n<tr title="Maximum turning speed in degrees per second">\n<td class="infobox-data-title"><b>Max. turn speed</b>\n</td>\n<td style="padding-right: 1em;">{turnRate} deg/s\n</td></tr>\n<tr title="Maximum speed of this ship on thrusters">\n<td class="infobox-data-title"><b>Max. thrust speed</b>\n</td>\n<td style="padding-right: 1em;">{maxthrust} m/s\n</td></tr>\n<tr title="Maximum speed of this ship on cruise engines">\n<td class="infobox-data-title"><b>Max. cruise speed</b>\n</td>\n<td style="padding-right: 1em;">{maxCruise} m/s\n</td></tr>\n<tr title="Maximum reactor energy storage (capacitance)">\n<td class="infobox-data-title"><b>Power output</b>\n</td>\n<td style="padding-right: 1em;">{power_output} u\n</td></tr>\n<tr title="Amount of energy units generated per second">\n<td class="infobox-data-title"><b>Power recharge</b>\n</td>\n<td style="padding-right: 1em;">{power_recharge} u/s\n</td></tr>\n<tr>\n<td colspan="2" style="text-align: center; font-size: 14px; line-height: 18px; background: #555555; color: #ffffff">Additional Information\n</td></tr>\n<tr title="Price of the ship without any mounted equipment">\n<td class="infobox-data-title"><b>Ship price</b>\n</td>\n<td style="padding-right: 1em;">${hull_price}\n</td></tr>\n<tr title="Price of the ship with the default equipment">\n<td class="infobox-data-title"><b>Package price</b>\n</td>\n<td style="padding-right: 1em;">${package_price}\n</td></tr></table>\n'
        infocard = '<p>{infocard}\n</p><p><br/>\n</p>\n'
        handling = '<h2>Handling</h2>\n<ul>\n{handling}\n</ul>\n'
        hardpoints = '<h2>Hardpoints</h2>\n<ul>\n{hardpoints}\n</ul>\n'
        includes = '<h2>Purchase Includes</h2>\n<ul>\n{includes}\n</ul>'
        availability = '<h2>Availability</h2>\n<table class="wikitable collapsible collapsed">\n<tr>\n<th>Buying Locations\n</th></tr>\n<tr>\n<td>\n<table class="wikitable sortable">\n<tr>\n<th>Base</th>\n<th>Owner</th>\n<th>System</th>\n<th>Location\n</th></tr>\n{sold_at}\n</td></tr></table>\n</td></tr></table>'
        category = '\n[[Category: Ships]]\n{built_by}\n{class}'

        
        try:
            data["Ships"][name]
        except:
            print(f"Ship name {name} could not be found in database, quitting...")

        image = f'{data["Ships"][name]["nickname"]}.png'
    
        
        infobox = infobox.replace("{nickname}", data["Ships"][name]["nickname"])
        infobox = infobox.replace("{name}", data["Ships"][name]["longName"])
        infobox = infobox.replace("{image}", image)
        infobox = infobox.replace("{class}", data["Ships"][name]["type"])
        if data["Ships"][name]["built_by"] != "":
            if data["Ships"][name]["built_by"] in houses:
                infobox = infobox.replace("{built_by}", f'[[File:Flag-{data["Ships"][name]["built_by"].lower()}.png|19px]] {data["Ships"][name]["built_by"]}')
            else:
                infobox = infobox.replace("{built_by}", f'{data["Ships"][name]["built_by"]}')
        else:
            infobox = infobox.replace("{built_by}", "Unknown")

        infobox = infobox.replace("{techcompat}", data["Ships"][name]["techcompat"])
        infobox = infobox.replace("{gunCount}", str(data["Ships"][name]["gunCount"]))
        infobox = infobox.replace("{turretCount}", str(data["Ships"][name]["turretCount"]))
        other = ""
        if data["Ships"][name]["torpedoCount"] > 0:
            other = f'{other}<li>{data["Ships"][name]["torpedoCount"]}xCD/T</li>\n'
        if data["Ships"][name]["cmCount"] > 0:
            other = f'{other}<li>{data["Ships"][name]["cmCount"]}xCM</li>\n'
        if data["Ships"][name]["mineCount"] > 0:
            other = f'{other}<li>{data["Ships"][name]["mineCount"]}xM</li>\n'
        infobox = infobox.replace("{other}", other)
        if data["Ships"][name]["maxThrust"] > 0:
            infobox = infobox.replace("{maxthrust}", str(data["Ships"][name]["maxThrust"]))
        else:
            infobox = infobox.replace("{maxthrust} m/s", '<span style="color: #f7001d; font-style: italic;">Thruster not available</span>')
        infobox = infobox.replace("{hull}", "{:,}".format(data["Ships"][name]["hit_pts"]))
        infobox = infobox.replace("{cargo}", "{:,}".format(data["Ships"][name]["hold_size"]))
        infobox = infobox.replace("{batteries}", "{:,}".format(data["Ships"][name]["bat_limit"]))
        infobox = infobox.replace("{bots}", "{:,}".format(data["Ships"][name]["bot_limit"]))
        infobox = infobox.replace("{maxwep}", str(data["Ships"][name]["maxClass"]))
        infobox = infobox.replace("{maxShield}", "{:,}".format(data["Ships"][name]["maxShield"]))
        infobox = infobox.replace("{impulse}", "{:,}".format(data["Ships"][name]["impulse_speed"]))
        infobox = infobox.replace("{turnRate}", "{:,}".format(data["Ships"][name]["turnRate"]))
        infobox = infobox.replace("{power_output}", "{:,}".format(data["Ships"][name]["power_output"]))
        infobox = infobox.replace("{maxCruise}", "{:,}".format(data["Ships"][name]["maxCruise"]))
        infobox = infobox.replace("{power_recharge}", "{:,}".format(data["Ships"][name]["power_recharge"]))
        infobox = infobox.replace("{hull_price}", "{:,}".format(data["Ships"][name]["hull_price"]))
        infobox = infobox.replace("{package_price}", "{:,}".format(data["Ships"][name]["package_price"]))

        info = data["Ships"][name]["infocard"].split("\n", 1)[1]
        while True:
            if info[0].isspace():
                info = info[1:len(info)]
            else:
                break
        infocard = infocard.replace("{infocard}", info)

        handleList = data["Ships"][name]["maneuverability"].split("\n")
        handle = ""
        if data["Ships"][name]["mustUseMoors"] == True:
            handle = "<li>This ship is too large to use docking bays, it must use mooring points.</li>\n"
        for entry in handleList:
            if entry != "":
                handle = f"{handle}<li>{entry}</li>\n"
        handling = handling.replace("{handling}", handle)

        harderpoint = ""
        for hardpoint in data["Ships"][name]["hardpoints"]:
            title = hardpoint.split(":")[0]
            count = hardpoint.split(":")[1]
            harderpoint = f"{harderpoint}<li>{count}x {title}</li>\n"
        hardpoints = hardpoints.replace("{hardpoints}", harderpoint)

        included = ""
        for title, price in data["Ships"][name]["equipment"]:
            included = f'{included}<li>{title} (${"{:,}".format(price)})</li>\n'
        includes = includes.replace("{includes}", included)

        sold_at = ""
        for base, owner, system, region in data["Ships"][name]["sold_at"]:
            region = "Independent Worlds" if region == "Independent" else region
            sold_at = f"{sold_at}<tr><td>{base}</td>\n<td>{owner}</td>\n<td>{system}</td>\n<td>{region}</td></tr>\n"
        availability = availability.replace("{sold_at}", sold_at)

        if data["Ships"][name]["built_by"] != "":
            category = category.replace("{built_by}", f'[[Category: {data["Ships"][name]["built_by"]}]]')
        else:
            category = category.replace("{built_by}", '')
        category = category.replace("{class}", f'[[Category: {data["Ships"][name]["type"]}]]')


        return f"{infobox}{infocard}{handling}{hardpoints}{includes}{availability}{category}"
    elif "sys" in template.lower():
        infobox = '__NOTOC__\n<table class="infobox bordered" style="float: right; width: 270px; font-size: 90%; line-height: 110%; margin-left: 1em; margin-bottom: 1em; border: 1px solid #aaa;" cellpadding="3">\n<tr>\n<td colspan="2" class="infobox-name" style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 185%; font-weight: 500; text-decoration: underline; text-align: center; line-height: 1.5em;">{name}\n</td></tr>\n<tr>\n<td colspan="2" style="text-align: center;"><div class="center"><div class="floatnone">[[File:{image}|center|220px]]</div></div>\n</td></tr>\n<tr>\n<td colspan="2" class="infobox-section" style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 150%; font-weight: 500; text-decoration: underline; text-align: center; line-height: 1.5em;">System\n</td></tr>\n<tr title="">\n<td class="infobox-data-title"><b>Governing House</b>\n</td>\n<td>{governingHouse}\n</td></tr>\n<tr title="">\n<td class="infobox-data-title"><b>Region</b>\n</td>\n<td>{region}\n</td></tr>\n<tr title="">\n<td class="infobox-data-title"><b>Connected Systems</b>\n</td>\n<td>{systems}\n</td></tr></table>\n'
        infocard = '<p>{infocard}</p>\n<br style="clear: both; height: 0px;" />\n</p>\n'
        overview = '<h1><span class="mw-headline" id="System_Overview">System Overview</span></h1>\n<hr>\n<table style="width: 100%;">\n<tr>\n<td style="width: 33%; vertical-align: top; border-right: 1px dotted #999999; padding: .5em 1em; margin: 1em;">\n<div style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 150%; text-align: center; line-height: 1.5em; border-bottom-width: 1px; border-bottom-color: #AAAAAA; border-bottom-style: solid;">Astronomical Bodies</div>\n<div style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 133%; text-decoration: underline; line-height: 1.5em; padding-top: .5em;">Stellar Objects</div>\n{suns}\n<div style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 133%; text-decoration: underline; line-height: 1.5em; padding-top: .5em;">Planetary Objects</div>\n{planets}\n<div style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 133%; text-decoration: underline; line-height: 1.5em; padding-top: .5em;">Nebulae &amp; Asteroids</div>\n{fields}\n</td>\n<td style="width: 33%; vertical-align: top; border-right: 1px dotted #999999; padding: .5em 1em; margin: 1em;">\n<div style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 150%; text-align: center; line-height: 1.5em; border-bottom-width: 1px; border-bottom-color: #AAAAAA; border-bottom-style: solid;">Industrial Development</div>\n<div style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 133%; text-decoration: underline; line-height: 1.5em; padding-top: .5em;">Space Stations</div>\n{stations}\n<li class="mw-empty-elt"></li></ul>\n<div style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 133%; text-decoration: underline; line-height: 1.5em; padding-top: .5em;">Commodity Mining</div>\n{mining}\n</td>\n<td style="width: 33%; vertical-align: top; padding: .5em 1em; margin: 1em;">\n<div style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 150%; text-align: center; line-height: 1.5em; border-bottom-width: 1px; border-bottom-color: #AAAAAA; border-bottom-style: solid;">Faction Presence</div>\n<div style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 133%; text-decoration: underline; line-height: 1.5em; padding-top: .5em;">Lawful Factions</div>\n{lawfuls}\n<div style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 133%; text-decoration: underline; line-height: 1.5em; padding-top: .5em;">Corporations &amp; Guilds</div>\n{corps}\n<div style="font-family: Agency FB,​Verdana,​Arial,​sans-serif; font-size: 133%; text-decoration: underline; line-height: 1.5em; padding-top: .5em;">Unlawful Factions</div>\n{unlawfuls}\n</td></tr></table>\n'
        navmap = '<p><br style="clear: both; height: 0px;" />\n</p>\n<h1><span class="mw-headline" id="System_Map">System Map</span></h1>\n<hr>\n<p>[https://space.discoverygc.com/navmap/#q={name} Navmap]\n</p>\n'
        AoI = "<h1>Areas of Interest</h1>\n<hr>\n"
        nebulae = "<h2>Nebulae</h2>\n\n{nebulae}\n"
        asteroids = "<h2>Asteroid Fields</h2>\n\n{asteroids}\n"
        gates = '<h1>Jump Gates/Holes</h1>\n<hr>\n<table class="wikitable collapsible collapsed">\n<tr>\n<th>Jump Hole/Gate Locations \n</th></tr>\n<tr>\n<td>\n<table class="wikitable sortable">\n<tr>\n<th>Target System</th>\n<th>Location</th>\n<th>Type</th></tr>\n{gates}\n</td></tr></table>\n</td></tr></table>'
        category = '\n[[Category: Systems]]\n{region}'

        try:
            if data["Systems"][name]:
                pass
        except:
            print(f"System {name} could not be found in database, quitting...")
            sys.exit()

        infobox = infobox.replace("{name}", name)
        infobox = infobox.replace("{image}", f'{data["Systems"][name]["nickname"]}.png')
        
        region = data["Systems"][name]["region"]
        if region == "Independent": region = "Independent Worlds"
        if region in config["settings"]["houses"]: 
            infobox = infobox.replace("{governingHouse}", f'[[File:Flag-{region.lower()}.png|19px]] {region}')
        else:
            infobox = infobox.replace("{governingHouse}", 'Independent')
        infobox = infobox.replace("{region}", region)
        temp = ""        
        for neighbor in data["Systems"][name]["neighbors"]:
            temp = f"{temp}[[{neighbor}]]<br/>"
        infobox = infobox.replace("{systems}", temp)

        if exists(f'../infocards/systems/{data["Systems"][name]["nickname"]}.txt'):
            with open(f'../infocards/systems/{data["Systems"][name]["nickname"]}.txt', 'r') as f:
                info = f.read()
            infocard = infocard.replace("{infocard}", info.replace("\n", "<p>"))
        else:
            infocard = infocard.replace("{infocard}", "<i>No description available.</i>")
        
        temp = ""
        for star, card in data["Systems"][name]["stars"].items():
            temp = f"{temp}<b>{star}</b><ul>"
            card = card[:-1]
            card = card.split("\n")
            for x in card: temp = f'{temp}<li>{x}</li>\n'
            temp = f"{temp}</ul>"
        overview = overview.replace("{suns}", temp)

        planets = "<ul>"
        for planet, nickname, owner in data["Systems"][name]["planets"]:
            inhabited = f"{owner}" if owner != "" else "Uninhabited"
            planets = f"{planets}<li><b>[[{planet}]]</b> -- <i>{inhabited}</i></li>\n"
        overview = overview.replace("{planets}", f"{planets}</ul>")

        
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
        for base, dicty in data["Systems"][name]["bases"].items():
            if dicty["type"] != "<class 'flint.entities.solars.PlanetaryBase'>":
                bases.append([base, dicty["owner"]])
            if dicty["owner"] in [x[0] for x in config["settings"]["corporations"]]:
                corporateFactions.append(dicty["owner"])
            elif dicty["factionLegality"] == "Lawful":
                lawfulFactions.append(dicty["owner"])
            elif dicty["factionLegality"] == "Unlawful":
                unlawfulFactions.append(dicty["owner"])
        stations = "<ul>"
        for base, owner in bases:
            stations = f"{stations}<li><b>[[{base}]]</b> -- <i>{owner}</i></li>\n"
        overview = overview.replace("{stations}", f"{stations}</ul>")

        mineableCommodities = "<ul>"
        mineableCommodity = []
        for doesnt, matter, commodity in data["Systems"][name]["asteroids"]:
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
        for target, type, location in data["Systems"][name]["holes"]:
            jumps = f"{jumps}<tr><td>[[{target}]]</td>\n<td>{type}</td>\n<td>{location}</td></tr>\n"
        gates = gates.replace("{gates}", jumps)

        if region != "":
            category = category.replace("{region}", f'[[Category: {region}]]')
        else:
            category = category.replace("{region}", '')

        return f"{infobox}{infocard}{overview}{navmap}{AoI}{nebulae}{asteroids}{gates}{category}"
    elif "base" in template.lower():
        template = '__NOTOC__\n<table class="infobox bordered" style="float: right; margin-left: 1em; margin-bottom: 10px; width: 250px; font-size: 11px; line-height: 14px; border: 1px solid #555555;" cellpadding="3">\n\n<tr>\n<td colspan="2" style="text-align: center; font-size: 16px; line-height: 18px; background: #555555; color: #ffffff", title="{nickname}"><b>{name}</b>\n</td>\n</tr>\n<tr>\n<td colspan="2" style="text-align: center; border: 1px solid #555555;">\n<div class="center">\n<div class="floatnone">[[File:{image}|250px]]</div>\n</div>\n</td>\n</tr>\n<tr>\n<td colspan="2" style="text-align: center; font-size: 14px; line-height: 18px; background: #555555; color: #ffffff">Owner\n</td>\n</tr>\n<tr>\n<td colspan="2" style="text-align: center; font-size: 12px; line-height: 18px;">{owner}\n</td>\n</tr>\n<tr>\n<td colspan="2" style="text-align: center; font-size: 14px; line-height: 18px; background: #555555; color: #ffffff">Location\n</td>\n</tr>\n<tr>\n<td colspan="2" style="text-align: center; font-size: 12px; line-height: 18px;">{location}\n</td>\n</tr>\n<tr>\n<td colspan="2" style="text-align: center; font-size: 14px; line-height: 18px; background: #555555; color: #ffffff">Technical Data\n</td>\n</tr>\n<tr>\n<td class="infobox-data-title"><b>Class</b>\n</td>\n<td style="padding-right: 1em;">Zeus\n</td>\n</tr>\n\n</table>\n\n{infocard}\n\n<h2>Bribes & Missions Offered</h2>\n\n<table style="float: left; margin-bottom: 10px; margin-left: 1em; width: 25%; border: 1px solid #555555;" cellpadding="3">\n\n<tr>\n<td style="text-align: center; font-size: larger; background: #555555; color: #ffffff;"><b>Bribes</b>\n</td>\n</tr>\n<tr>\n<td style="padding-bottom: 7px;">\n<ul>\n{bribes}\n</ul>\n</td>\n</tr>\n</table>\n\n<table style="float: left; margin-bottom: 10px; margin-left: 1em; width: 25%; border: 1px solid #555555;" cellpadding="3">\n\n<tr>\n<td style="text-align: center; font-size: larger; background: #555555; color: #ffffff;"><b>Missions</b>\n</td>\n</tr>\n<tr>\n<td style="padding-bottom: 7px;">\n<ul>\n{missions}\n</ul>\n</td>\n</tr>\n</table>\n\n<p><br style="clear: both; height: 0px;" />\n</p>\n<h2>Commodities</h2>\n\n<table style="float: left; margin-bottom: 10px; margin-left: 1em; width: 25%; border: 1px solid #47505a;" cellpadding="3">\n\n<tr>\n<td style="text-align: center; font-size: larger; background: #555555; color: #ffffff;"><b>Imports</b>\n</td>\n</tr>\n<tr>\n<td style="padding-bottom: 7px;">\n<ul>\n{imports}\n</ul>\n</td>\n</tr>\n</table>\n\n<table style="float: left; margin-bottom: 10px; margin-left: 1em; width: 25%; border: 1px solid #555555;" cellpadding="3">\n\n<tr>\n<td style="text-align: center; font-size: larger; background: #555555; color: #ffffff;"><b>Exports</b>\n</td>\n</tr>\n<tr>\n<td style="padding-bottom: 7px;">\n<ul>\n{exports}\n</ul>\n</td>\n</tr>\n</table>\n<p><br style="clear: both; height: 0px;" />\n</p>\n<h2>Ships sold</h2>\n<ul>\n{ships}\n</ul>\n\n<p><br style="clear: both; height: 0px;" />\n</p>\n<h2>Rumors</h2>\n\n{rumors}'

loadedData = loadData("flData.json")
configData = loadData("config.json")
sources = {}

for name, attributes in loadedData["Systems"].items():
    source = main(template = "System", data = loadedData, config = configData, name = name)
    sources[name] = source
    print(f"Processed {name}")
for name, attributes in loadedData["Ships"].items():
    source = main(template = "Ship", data = loadedData, config = configData, name = name)        
    sources[name] = source
    print(f"Processed {name}")
with open("wikitext.json", "w") as f:
    json.dump(sources, f, indent=1)