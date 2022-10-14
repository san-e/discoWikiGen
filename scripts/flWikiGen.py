import flint as fl
import discoTechCompat as tech
from json import dump, load
from time import time
from math import pi
from sys import argv
from os import getcwd, makedirs
from os.path import exists, basename
from PIL import Image
from io import BytesIO
from datetime import datetime

version = ""#input("Enter game version: ")

with open(f"{getcwd()}\\config.json", "r") as file:
    config = load(file)
oorp = config["wikiGen"]["oorpSystems"]
shipBuilders = config["wikiGen"]["shipBuilders"]

try:
    if exists(argv[1]):
        if exists(argv[1] + "\\EXE\\freelancer.exe"):
            fl.set_install_path(argv[1])
    else:
        print("Invalid directory")
        quit()
except IndexError:
    print(f"Path to Freelancer directory not given.\nUsage: python {basename(__file__)} [path_to_freelancer]")
    quit()

if not exists(config["wikiGen"]["dumpedData"]):
    for folder in config["wikiGen"]["createDir"]:
        makedirs(folder)

# LOOKUP TABLES
gun_table = {x.nickname: x.name() for x in fl.equipment if str(type(x)) == "<class 'flint.entities.equipment.Gun'>" and x.is_valid()}
base_table = {base.nickname: base.name() for base in fl.bases if base.has_solar()}
commodity_table = {commodity.nickname: commodity.name() for commodity in fl.commodities}
infocardMap = fl.interface.get_infocardmap()

logs = []

def degree(x):
    degree = (x * 180) / pi
    return degree

def getMineableCommodites(path):
    content = fl.formats.ini.parse(f"{argv[1]}\\DATA\\{path}")
    for header, attributes in content:
        if header.lower() == "lootablezone":
            if "asteroid_loot_commodity" in attributes.keys():
                return commodity_table[attributes["asteroid_loot_commodity"]]
    return None

def get_ships(definitions: dict) -> dict:
    print("Reading ship data...")
    ships = {}
    for ship in fl.ships:
        if not "_npc" in ship.nickname and ship.sold_at():
            try:
                built_by = ""
                for shorthand, fullName in shipBuilders.items():
                    if shorthand in ship.nickname:
                        built_by = fullName
                        break

             
                equipment = []
                for x in ship.equipment():
                    equipment.append([x.name(), x.price()])

                try:
                    hull_price = ship.hull().price
                except:
                    hull_price = 0
                
                try:
                    try:
                        if len(ship.hardpoints()["hpshield01"]) > 1:
                            for x in ship.hardpoints()["hpshield01"]:
                                if int(x.nickname[-1]) > maxShield:
                                    maxShield = int(x.nickname[-1])
                        else:
                            maxShield = int(ship.hardpoints()["hpshield01"][0].nickname[-1])
                    except:
                        if len(ship.hardpoints()["hpshield02"]) > 1:
                            for x in ship.hardpoints()["hpshield02"]:
                                if int(x.nickname[-1]) > maxShield:
                                    maxShield = int(x.nickname[-1])
                        else:
                            maxShield = int(ship.hardpoints()["hpshield02"][0].nickname[-1])
                except:
                    maxShield = 0

                gunCount = len([x for x in ship.hardpoints() if 'weapon' in x.lower()])
                turretCount = len([x for x in ship.hardpoints() if 'turret' in x.lower()])
                torpedoCount = len([x for x in ship.hardpoints() if 'torpedo' in x.lower()])
                mineCount = len([x for x in ship.hardpoints() if 'mine' in x.lower()])
                cmCount = len([x for x in ship.hardpoints() if 'cm' in x.lower()])
                thrusterCount = len([x for x in ship.hardpoints() if 'thruster' in x.lower()])
                maxClass = {"1" : 0, "2" : 0, "3" : 0, "4" : 0, "5" : 0, "6" : 0, "7" : 0, "8" : 0, "9" : 0, "10" : 0}
                for x in ship.hardpoints().values():
                    try:
                        if "gun_special_1" in x[0].nickname:
                            maxClass["1"] += 1
                        elif "gun_special_2" in x[0].nickname:
                            maxClass["2"] += 1
                        elif "gun_special_3" in x[0].nickname:
                            maxClass["3"] += 1
                        elif "gun_special_4" in x[0].nickname:
                            maxClass["4"] += 1
                        elif "gun_special_5" in x[0].nickname:
                            maxClass["5"] += 1
                        elif "gun_special_6" in x[0].nickname:
                            maxClass["6"] += 1
                        elif "gun_special_7" in x[0].nickname:
                            maxClass["7"] += 1
                        elif "gun_special_8" in x[0].nickname:
                            maxClass["8"] += 1
                        elif "gun_special_9" in x[0].nickname:
                            maxClass["9"] += 1
                        elif "hp_turret_special_1" == x[0].nickname:
                            maxClass["1"] += 1
                        elif "turret_special_2" in x[0].nickname:
                            maxClass["2"] += 1
                        elif "turret_special_3" in x[0].nickname:
                            maxClass["3"] += 1
                        elif "turret_special_4" in x[0].nickname:
                            maxClass["4"] += 1    
                        elif "turret_special_5" in x[0].nickname:
                            maxClass["5"] += 1                                                     
                        elif "turret_special_6" in x[0].nickname:
                            maxClass["6"] += 1
                        elif "turret_special_7" in x[0].nickname:
                            maxClass["7"] += 1                            
                        elif "turret_special_9" in x[0].nickname:
                            maxClass["9"] += 1
                        elif "hp_turret_special_10" == x[0].nickname:
                            maxClass["10"] += 1
                        elif "turret_special_8" in x[0].nickname:
                            maxClass["8"] += 1                                                                                  
                    except AttributeError:
                        pass                    

                delete = []
                for x in maxClass.items():
                    if x[1] == 0:
                        delete.append(x[0])
                for x in delete:
                    del maxClass[x]                

                try:
                    power_output = ship.power_core().capacity
                    power_recharge = ship.power_core().charge_rate
                except:
                    power_output = 0
                    power_recharge = 0

                hardpoints = []
                for x in ship.hardpoints().values():
                    if x[0].name() != x[0].nickname:
                        hardpoints.append(x[0].name())
                tempHardpoints = []
                for x in hardpoints:
                    tempHardpoints.append(f"{x}:{hardpoints.count(x)}")

                hardpoints = list( dict.fromkeys(tempHardpoints) ) #remove duplicates

                try:
                    maxClass = list(maxClass.keys())[-1]
                except:
                    maxClass = 0

                try:
                    infocardMan = ship.infocard('plain').split("Maneuverability")[1][2:][:-1]
                except:
                    infocardMan = ""
                
                techcompat = ""
                for x in definitions.items():
                    if ship.nickname in x[1]:
                        techcompat = x[0]

                turnRate = degree(ship.turn_rate())
                angularDistanceInTime = ship.angular_distance_in_time(0.5)
                responseTime = ship.response()
                # Time to turn 180 ~ 180 / turnRate

                thruster_force = 72000
                engine = ship.engine()
                linear_drag = ship.linear_drag + engine.linear_drag if engine else ship.linear_drag
                force = thruster_force + ship.engine().max_force
                maxThrust = int(force / linear_drag) if thrusterCount > 0 else 0

                mustUseMoors = False if ship.mission_property == 'can_use_berths' else True

                maxCruise = ship.engine().cruise_speed if ship.engine().cruise_speed != 0 else 350
                if isinstance(maxCruise, list):
                    maxCruise = maxCruise[0]

                infocard = ship.infocard('plain').split("<p>")[0]

                icon = ship.icon()
                image = Image.open(BytesIO(icon))
                if image.size != (64, 64):
                    image.save(f'../dumpedData/images/ships/{ship.nickname}.png')
                else:
                    image.resize((128,128)).save(f'../dumpedData/images/ships/{ship.nickname}.png')
                    

                ships[ship.nickname] = {
                    "name" : ship.name(),
                    "longName" : ship.infocard('plain').split("\n")[0],
                    "maneuverability" : infocardMan,
                    "built_by" : built_by,
                    "techcompat": techcompat,
                    "type" : ship.type(),
                    "maxClass" : maxClass,
                    "maxShield" : maxShield,
                    "infocard" : infocard.replace("&nbsp;", ""),
                    "hull_price" : hull_price,
                    "package_price" : ship.price(),
                    "impulse_speed" : int(ship.impulse_speed()),
                    "maxThrust" : maxThrust,
                    "hit_pts" : ship.hit_pts,
                    "hold_size" : ship.hold_size,
                    "gunCount" : gunCount, 
                    "thrusterCount" : thrusterCount,
                    "turretCount" : turretCount,
                    "torpedoCount" : torpedoCount,
                    "mineCount" : mineCount,
                    "cmCount" : cmCount,
                    "bot_limit" : ship.nanobot_limit,
                    "bat_limit" : ship.shield_battery_limit,
                    "power_output" : power_output,
                    "maxCruise" : maxCruise,
                    "power_recharge" : power_recharge,
                    "turnRate" : round(turnRate, 2),
                    "angularDistance0.5" : angularDistanceInTime,
                    "responseTime" : responseTime,
                    "mustUseMoors" : mustUseMoors,
                    "equipment" : equipment,
                    "sold_at" : [[base.name(), base.owner().name(), base.system_().name(), base.system_().region()] for base in ship.sold_at() if base.has_solar() and base.system_().nickname not in oorp],
                    "hardpoints" : hardpoints,
                    "time": datetime.now().strftime('Page generated on the %d/%m/%Y at %H:%M:%S')
                }
            except TypeError as e:
                logs.append({ship: e})
    return ships

def get_bases() -> dict:
    print("Reading base data...")
    bases = {}
    for base in fl.bases:
        if base.has_solar() and base.system_().nickname not in config["wikiGen"]["oorpSystems"]:
            try:
                ships_sold = [[ship.name(), ship.type(), price] for ship, price in base.sells_ships().items()]
                specifications = fl.formats.dll.lookup_as_html(base.solar().ids_info)
                try:
                    synopsis = fl.formats.dll.lookup_as_html(infocardMap[base.solar().ids_info])
                except (IndexError, KeyError):
                    synopsis = fl.formats.dll.lookup_as_html(base.solar().ids_info + 1)
 
                bases[base.nickname] = {
                    "name": base.name(),
                    "specs": specifications,
                    "infocard" : synopsis,
                    "owner" : base.owner().name(),
                    "system" : base.system_().name(),
                    "region": base.system_().region(),
                    "sector" : base.sector(),
                    "bribes": [faction.name() for faction in base.bribes()],
                    "missions": [faction.name() for faction in base.missions()],
                    "rumors": {fl.factions[faction].name(): rumor for faction, rumor in base.rumors().items()},
                    "commodities_buying": [x.name() for x in base.buys_commodities()],
                    "commodities_selling": [x.name() for x in base.sells_commodities()],
                    "ships_sold" : ships_sold,
                    "time": datetime.now().strftime('Page generated on the %d/%m/%Y at %H:%M:%S')
                }
            except (TypeError, AttributeError) as e:
                logs.append({base: e})
    return bases

def get_systems() -> dict:
    print("Reading system data...")
    systems = {}
    for system in fl.systems:
        try:
            if system.nickname not in oorp:
                bases = {}
                planets = []
                holes = []
                neighbors = []
                zones = []
                stars = {}
                nebulae = []
                asteroids = []
                for solar_type, attributes in system.contents_raw():
                    if solar_type.lower() == "nebula":
                        try:
                            nebulae.append([attributes['zone'], attributes['file']])
                        except KeyError:
                            pass
                    elif solar_type.lower() == "asteroids":
                        try:
                            asteroids.append([attributes['zone'], attributes['file']])
                        except KeyError:
                            pass
                for x in asteroids:
                    x.append(getMineableCommodites(x[1]))
                for base in system.bases():
                    bases[base.name()] = {
                        "owner": base.owner().name(),
                        "factionLegality": base.owner().legality(),
                        "type": str(type(base))
                    }
                for planet in system.planets():
                    if str(type(planet)) == "<class 'flint.entities.solars.PlanetaryBase'>":
                        planets.append([
                            planet.name(),
                            planet.nickname,
                            planet.owner().name() if len(planet.owner().name()) <= 20 else planet.owner().short_name()
                            ])
                    else:
                        planets.append([planet.name(), planet.nickname, ""])
                for x in system.connections():
                    name = fl.systems[x.goto[0]].name()
                    neighbors.append(name)
                    holes.append([name, x.type(), x.sector()])
                    
                    
                for x in system.zones():
                    zones.append([
                        x.name(),
                        x.nickname,
                        x.infocard('html') if type(x.infocard('html')) == list else x.infocard('html')])
                for star in system.stars():
                    stars[star.name()] = star.infocard('plain')
                neighbors = [x for x in neighbors if x != system.name()]
                neighbors = list(dict.fromkeys(neighbors))

                systems[system.nickname] = {
                    "name" : system.name(),
                    "infocard" : system.infocard('plain'),
                    "region" : system.region() if system.region() != "Independent" else "Independent Worlds",
                    "bases" : bases,
                    "planets": planets,
                    "stars": stars,
                    "holes" : holes,
                    "neighbors" : neighbors,
                    "zones" : zones,
                    "nebulae": nebulae,
                    "asteroids": asteroids,
                    "time": datetime.now().strftime('Page generated on the %d/%m/%Y at %H:%M:%S')
                }
        except Exception as e:
            logs.append({system: e})
    return systems

def get_factions() -> dict:
    print("Reading faction data...")
    factions = {}
    for faction in fl.factions:
        if faction.nickname not in faction.name() and not faction.name().isspace():
            alignment = "Corporation" if faction.name() in config["pageGen"]["corporations"] else faction.legality()

            reps = {faction.name(): rep for faction, rep in faction.rep_sheet().items() if rep}
            reps = sorted(reps.items(), key=lambda x:x[1])
            reps = dict(reps)

            factions[faction.nickname] = {
                "name": faction.name(),
                "alignment": alignment,
                "infocard": '<p style="padding: 0px; margin: 0px;">' + faction.infocard().replace("<p>", '<p style="padding: 0px; margin: 0px;">'),
                "ships": [[ship.name(), ship.type()] for nickname, ship in faction.ships().items()],
                "bases": [[base.name(), base.owner().name(), base.system_().name(), base.system_().region()] for nickname, base in faction.bases().items() if base.system_().nickname not in oorp],
                "bribes": [[base.name(), base.owner().name(), base.system_().name(), base.system_().region()] for nickname, base in faction.bribes().items() if base.system_().nickname not in oorp],
                "repsheet": reps,
                "rumors": {fl.bases[base].name(): text for base, text in faction.rumors().items()},
                "time": datetime.now().strftime('Page generated on the %d/%m/%Y at %H:%M:%S')
            }
    return factions

def get_commodities() -> dict:
    print("Reading commodity data...")
    commodities = {}
    for commodity in fl.commodities:
        try:
            icon = commodity.icon()
            image = Image.open(BytesIO(icon))
            if image.size != (64, 64):
                image.save(f'../dumpedData/images/commodities/{commodity.nickname}.png')
            else:
                image.resize((128,128)).save(f'../dumpedData/images/commodities/{commodity.nickname}.png')
        except FileNotFoundError:
            pass

        commodities[commodity.nickname] = {
            "name": commodity.name(),
            "infocard": commodity.infocard(),
            "volume": commodity.volume,
            "decay" : commodity.decay_per_second,
            "defaultPrice": commodity.price(),
            "boughtAt": [[base.name(), base.owner().name(), base.system_().name(), base.system_().region(), price] for base, price in commodity.bought_at().items() if base.system_().nickname not in oorp],
            "soldAt": [[base.name(), base.owner().name(), base.system_().name(), base.system_().region(), price] for base, price in commodity.sold_at().items() if base.system_().nickname not in oorp],
            "time": datetime.now().strftime('This page was generated on the %d/%m/%Y at %H:%M:%S. Server-side data may be changed on the server at any time, without any notice to the user community. The only authoritative source for in-game data is the game itself.')
        }
    return commodities

if __name__ == "__main__":
    filename = "flData.json"
    print("Reading game files...")
    startTime = time()
    data = {"README" : f"This file was automatically generated by {basename(__file__)}. Do not edit unless you know what you're doing!", "Version": version,
            "Ships" : get_ships(definitions = tech.get_definitions()),
            "Systems" : get_systems(),
            "Bases" : get_bases(),
            "Factions": get_factions(),
            "Commodities": get_commodities()
            }
    print(f"Game files read, writing {filename}...")
    with open(f'../dumpedData/{filename}', 'w') as f:
        dump(data, f, indent=1)
    endTime = time()
    print(f"Done.\nReading and writing took {round(endTime-startTime, 2)}s")
    print(logs)
