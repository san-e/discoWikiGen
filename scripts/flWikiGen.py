import flint as fl
import discoTechCompat as tech
from json import dump, load
from time import perf_counter
from math import pi, inf
from sys import argv
from os import getcwd, makedirs, listdir, remove
from os.path import exists, basename, splitext, isfile, join, abspath
from PIL import Image
from io import BytesIO
from datetime import datetime
import pytz
import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import cv2
import subprocess
import time

logging.basicConfig(
    level=logging.ERROR,
    filename=datetime.now(tz=pytz.UTC).strftime("./logs/%d-%m-%Y_%Hh%Mm%Ss.log"),
)

version = ""  # input("Enter game version: ")

with open("./config.json", "r") as file:
    config = load(file)
with open("./secret.json", "r") as file:
    secrets = load(file)
LLEDITSCRIPT = secrets["librelancer"] + "/lleditscript.exe"
EXPORTER = "./exporter.cs-script"
oorp = config["wikiGen"]["oorpSystems"]
shipBuilders = config["wikiGen"]["shipBuilders"]

if not exists(config["wikiGen"]["dumpedData"]):
    for folder in config["wikiGen"]["createDir"]:
        makedirs(folder)

flintClasses = {
    "PlanetaryBase": fl.entities.solars.PlanetaryBase,
    "Planet": fl.entities.solars.Planet,
    "BaseSolar": fl.entities.solars.BaseSolar,
    "Star": fl.entities.solars.Star,
    "Zone": fl.entities.solars.Zone,
    "TradeLaneRing": fl.entities.solars.TradeLaneRing,
    "Object": fl.entities.solars.Object,
    "Jump": fl.entities.solars.Jump,
    "Gun": fl.entities.equipment.Gun,
    "MineDropper": fl.entities.equipment.MineDropper,
    "Thruster": fl.entities.equipment.Thruster,
    "CloakingDevice": fl.entities.equipment.CloakingDevice,
    "Power": fl.entities.equipment.Power,
    "Scanner": fl.entities.equipment.Scanner,
    "CounterMeasureDropper": fl.entities.equipment.CounterMeasureDropper,
    "Engine": fl.entities.equipment.Engine,
    "Armor": fl.entities.equipment.Armor,
    "CargoPod": fl.entities.equipment.CargoPod,
    "ShieldGenerator": fl.entities.equipment.ShieldGenerator,
}

EntitySet = fl.entities.EntitySet
ini = fl.formats.ini
dll = fl.formats.dll


def load_all_infocards():  # probably extremely inefficient, since loading just one resource from each dll should be enough, but w/e
    for i in range(65539 * len(fl.paths.dlls)):
        dll.lookup(i)


def apply_server_infocard_override():
    load_all_infocards()

    infocards = dict(
        ini.parse("./server_config/infocard_overrides.cfg", infocard_override=True)
    ).get("IDStrings")

    for id, value in infocards.items():
        dll.override_resource(int(id), value)

    # verify things worked
    for id, value in infocards.items():
        assert dll.lookup(int(id)) == value


def degree(x):
    degree = (x * 180) / pi
    return degree


def get_mineable_commodites(path):
    content = ini.parse(fl.paths.construct_path(f"DATA/{path}"))
    for header, attributes in content:
        if header.lower() == "lootablezone":
            if "asteroid_loot_commodity" in attributes.keys():
                return commodity_table[attributes["asteroid_loot_commodity"]]
    return None


def filter_oorp_bases(bases):
    if not bases:
        return {}
    if type(bases) == list:
        return list(filter(lambda x: x.nickname not in oorpBases, bases))
    elif type(bases) == dict:
        return dict(filter(lambda x: x[0].nickname not in oorpBases, bases.items()))
    elif type(bases) == EntitySet:
        return EntitySet(filter(lambda x: x.nickname not in oorpBases, bases.values()))


processes = set()
MAX_PROCESSES = 50


def dump_model(model, materials, destination):
    if len(processes) > MAX_PROCESSES:
        for aaaa in processes:
            aaaa.wait()
        processes.clear()
    arguments = [LLEDITSCRIPT, EXPORTER, model]
    for material in materials:
        arguments.append(material)
    arguments.append(destination)
    p = subprocess.Popen(
        arguments, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    processes.add(p)


def save_icon(icon, name, folder):
    image = Image.open(BytesIO(icon))
    if image.size != (64, 64):
        image.save(f"../dumpedData/images/{folder}/{name}.png")
    else:
        image.resize((128, 128)).save(f"../dumpedData/images/{folder}/{name}.png")


def iconname(path):
    return splitext(basename(path))[0]


# ------------------------------------------------ #


def get_ships(definitions: dict, dumpModels: bool) -> dict:
    print("Reading ship data...")
    ships = {}
    for ship in fl.ships:
        if ship.nickname == "medium_miner":
            pass
        if (
            "_npc" in ship.nickname
            or not filter_oorp_bases(ship.sold_at())
            or not ship.materials()
        ):
            continue
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

            gunCount = len([x for x in ship.hardpoints() if "weapon" in x.lower()])
            turretCount = len([x for x in ship.hardpoints() if "turret" in x.lower()])
            torpedoCount = len([x for x in ship.hardpoints() if "torpedo" in x.lower()])
            mineCount = len([x for x in ship.hardpoints() if "mine" in x.lower()])
            cmCount = len([x for x in ship.hardpoints() if "cm" in x.lower()])
            thrusterCount = len(
                [x for x in ship.hardpoints() if "thruster" in x.lower()]
            )
            hp_types = {
                "hp_turret_special_10": 10,
                "hp_turret_special_9": 9,
                "hp_turret_special_8": 8,
                "hp_turret_special_7": 7,
                "hp_turret_special_6": 6,
                "hp_turret_special_5": 5,
                "hp_turret_special_4": 4,
                "hp_turret_special_3": 3,
                "hp_turret_special_2": 2,
                "hp_turret_special_1": 1,
                "hp_gun_special_10": 10,
                "hp_gun_special_9": 9,
                "hp_gun_special_8": 8,
                "hp_gun_special_7": 7,
                "hp_gun_special_6": 6,
                "hp_gun_special_5": 5,
                "hp_gun_special_4": 4,
                "hp_gun_special_3": 3,
                "hp_gun_special_2": 2,
                "hp_gun_special_1": 1,
            }

            maxClass = 0
            for hardpoint in {x[0].nickname for x in ship.hardpoints().values()}:
                if hp_types.get(hardpoint, 0) > maxClass:
                    maxClass = hp_types.get(hardpoint, 0)

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

            hardpoints = list(dict.fromkeys(tempHardpoints))  # remove duplicates

            comps = []
            components = {}
            if ship.type() == "Battlecruiser":
                try:
                    comps = (
                        ship.infocard("plain")
                        .split("Components")[1]
                        .strip()
                        .split("\n \n")
                    )
                    for component in comps:
                        temp = component.split("\n")
                        name = temp[0]
                        components[name] = temp[1:]
                except IndexError:
                    components = {}

            try:
                infocardMan = ship.infocard("plain").split("Maneuverability")[1].strip()
            except IndexError:
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
            linear_drag = (
                ship.linear_drag + engine.linear_drag if engine else ship.linear_drag
            )
            force = thruster_force + ship.engine().max_force
            maxThrust = int(force / linear_drag) if thrusterCount > 0 else 0

            mustUseMoors = not ship.mission_property == "can_use_berths"

            maxCruise = (
                ship.engine().cruise_speed if ship.engine().cruise_speed != 0 else 350
            )

            if isinstance(maxCruise, list):
                maxCruise = maxCruise[0]

            infocard = ship.infocard("plain").split("<p>")[0]

            # save_icon(icon=ship.icon(), name=ship.nickname, folder="ships")
            if dumpModels:
                dump_model(
                    ship.model(),
                    ship.materials(),
                    f"../dumpedData/models/{ship.nickname}.glb",
                )

            ships[ship.nickname] = {
                "name": ship.name(),
                "longName": ship.infocard("plain").split("\n")[0],
                "components": components,
                "maneuverability": infocardMan,
                "built_by": built_by,
                "techcompat": techcompat,
                "type": ship.type(),
                "maxClass": maxClass,
                "maxShield": maxShield,
                "infocard": infocard.replace("&nbsp;", ""),
                "hull_price": hull_price,
                "package_price": ship.price(),
                "impulse_speed": int(ship.impulse_speed()),
                "maxThrust": maxThrust,
                "hit_pts": ship.hit_pts,
                "hold_size": ship.hold_size,
                "gunCount": gunCount,
                "thrusterCount": thrusterCount,
                "turretCount": turretCount,
                "torpedoCount": torpedoCount,
                "mineCount": mineCount,
                "cmCount": cmCount,
                "bot_limit": ship.nanobot_limit,
                "bat_limit": ship.shield_battery_limit,
                "power_output": power_output,
                "maxCruise": maxCruise,
                "power_recharge": power_recharge,
                "turnRate": round(turnRate, 2),
                "angularDistance0.5": angularDistanceInTime,
                "responseTime": responseTime,
                "mustUseMoors": mustUseMoors,
                "equipment": equipment,
                "sold_at": [
                    [
                        base.name(),
                        base.owner().name(),
                        base.system_().name(),
                        base.system_().region(),
                    ]
                    for base in filter_oorp_bases(ship.sold_at())
                    if base.has_solar()
                ],
                "hardpoints": hardpoints,
                "time": datetime.now(tz=pytz.UTC).strftime(
                    "Page generated on the %d/%m/%Y at %H:%M:%S UTC"
                ),
            }

        except TypeError as e:
            logging.exception(f"Error occured for ship {ship.nickname}: {e}")
    return ships


def get_bases() -> dict:
    print("Reading base data...")
    bases = {}
    for base in fl.bases:
        if base.has_solar() and base.nickname not in oorpBases:
            try:
                ships_sold = [
                    [ship.name(), ship.type(), price]
                    for ship, price in base.sells_ships().items()
                ]
                specifications = fl.formats.dll.lookup_as_html(base.solar().ids_info)
                try:
                    synopsis = fl.formats.dll.lookup_as_html(
                        infocardMap[base.solar().ids_info]
                    )
                except (IndexError, KeyError):
                    synopsis = fl.formats.dll.lookup_as_html(base.solar().ids_info + 1)

                if base.news():
                    news = [
                        [newsitem.headline_(), newsitem.text_()]
                        for newsitem in base.news()
                    ]
                else:
                    news = []

                if base.bribes():
                    bribes = [faction.name() for faction in base.bribes()]
                else:
                    bribes = []

                bases[base.nickname] = {
                    "name": base.name(),
                    "specs": specifications,
                    "infocard": synopsis,
                    "owner": base.owner().name(),
                    "system": base.system_().name(),
                    "region": base.system_().region(),
                    "sector": base.sector(),
                    "bribes": bribes,
                    "missions": [faction.name() for faction in base.missions()],
                    "rumors": {
                        faction.name(): list(rumor)
                        for faction, rumor in base.rumors().items()
                    },
                    "news": news,
                    "commodities_buying": [
                        [commodity.name(), cost]
                        for commodity, cost in base.buys_commodities().items()
                    ],
                    "commodities_selling": [
                        [commodity.name(), cost]
                        for commodity, cost in base.sells_commodities().items()
                    ],
                    "ships_sold": ships_sold,
                    "time": datetime.now(tz=pytz.UTC).strftime(
                        "Page generated on the %d/%m/%Y at %H:%M:%S UTC"
                    ),
                }
            except (TypeError, AttributeError) as e:
                logging.exception(f"Error occured for base {base.nickname}: ")
    return bases


def get_systems(get_system_images=False) -> dict:
    print("Reading system data...")

    # Selenium setup
    if get_system_images:
        options = Options()
        options.binary_location = r"C:\Program Files\Mozilla Firefox\Firefox.exe"
        options.add_argument("-headless")
        options.set_preference("layout.css.devPixelsPerPx", "2.0")
        driver = webdriver.Firefox(options=options)
        driver.set_window_size(1920, 1080)
        driver.get(config["wikiGen"]["sysmapURL"])

    systems = {}
    solars = {}
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
                wrecks = []
                for solar_type, attributes in system.contents_raw():
                    if solar_type.lower() == "nebula":
                        try:
                            nebulae.append([attributes["zone"], attributes["file"]])
                        except KeyError:
                            pass
                    elif solar_type.lower() == "asteroids":
                        try:
                            asteroids.append([attributes["zone"], attributes["file"]])
                        except KeyError:
                            pass
                for x in asteroids:
                    x.append(get_mineable_commodites(x[1]))
                for base in system.bases():
                    bases[base.name()] = {
                        "owner": base.owner().name(),
                        "factionLegality": base.owner().legality(),
                        "type": str(type(base)),
                    }
                for planet in system.planets():
                    if type(planet) == flintClasses["PlanetaryBase"]:
                        owner = (
                            planet.owner().name()
                            if len(planet.owner().name()) <= 20
                            else planet.owner().short_name()
                        )
                        planets.append(
                            [
                                planet.name(),
                                owner if owner else "Uninhabited",
                            ]
                        )
                    else:
                        planets.append([planet.name(), "Uninhabited"])
                for x in system.connections():
                    name = fl.systems[x.goto[0]].name()
                    neighbors.append(name)
                    holes.append([name, x.type(), x.sector()])
                for x in system.zones():
                    zones.append(
                        [
                            x.name(),
                            x.nickname,
                            (
                                x.infocard("html")
                                if type(x.infocard("html")) == list
                                else x.infocard("html")
                            ),
                        ]
                    )
                for star in system.stars():
                    stars[star.name()] = star.infocard("plain")
                for w in system.wrecks():
                    if (
                        "surprise" in w.nickname.lower()
                        or "suprise" in w.nickname.lower()
                        or "secret" in w.nickname.lower()
                    ):
                        wrecks.append(
                            {
                                "name": w.name(),
                                "nickname": w.nickname,
                                "infocard": w.infocard(),
                                "sector": w.sector(),
                                "loot": [
                                    [equip.name(), amount] for equip, amount in w.loot()
                                ],
                            }
                        )
                neighbors = [x for x in neighbors if x != system.name()]
                neighbors = list(dict.fromkeys(neighbors))

                if get_system_images:
                    driver.get(f"{config['wikiGen']['sysmapURL']}#q={system.name()}")
                    driver.execute_script("location.reload(true);")
                    while (
                        driver.find_elements(By.CLASS_NAME, "loadingOverlay")
                        or driver.find_elements(By.CLASS_NAME, "loaderTitle")
                        or driver.find_elements(By.CLASS_NAME, "systemTitle")[0]
                        == "Sirius"
                    ):
                        pass
                    while (
                        driver.find_elements(By.CLASS_NAME, "systemTitle")[
                            0
                        ].get_attribute("innerHTML")
                        != system.name()
                    ):
                        driver.execute_script("location.reload(true);")
                        time.sleep(2)
                    sysmap = driver.find_elements(By.CLASS_NAME, "map")[0]
                    sysmap.screenshot(
                        f"../dumpedData/images/systems/{system.nickname}_map.png"
                    )

                systems[system.nickname] = {
                    "name": system.name(),
                    "infocard": system.infocard("plain"),
                    "region": (
                        system.region()
                        if system.region() != "Independent"
                        else "Independent Worlds"
                    ),
                    "bases": bases,
                    "planets": planets,
                    "stars": stars,
                    "holes": holes,
                    "neighbors": neighbors,
                    "zones": zones,
                    "nebulae": nebulae,
                    "asteroids": asteroids,
                    "wrecks": wrecks,
                    "time": datetime.now(tz=pytz.UTC).strftime(
                        "Page generated on the %d/%m/%Y at %H:%M:%S UTC"
                    ),
                }

                # get_solars()

        except Exception as e:
            logging.exception(f"Error occured for system {system.nickname}: ")
    if get_system_images:
        driver.quit()
    return systems


def get_factions() -> dict:
    print("Reading faction data...")
    factions = {}
    for faction in fl.factions:
        try:
            if faction.nickname not in faction.name() and not faction.name().isspace():
                alignment = (
                    "Corporation"
                    if faction.name() in config["pageGen"]["corporations"]
                    else faction.legality()
                )

                reps = {
                    faction.name(): rep
                    for faction, rep in faction.rep_sheet().items()
                    if rep
                }
                reps = sorted(reps.items(), key=lambda x: x[1])
                reps = dict(reps)

                factions[faction.nickname] = {
                    "name": faction.name(),
                    "shortName": faction.short_name(),
                    "alignment": alignment,
                    "infocard": '<p style="padding: 0px; margin: 0px;">'
                    + faction.infocard().replace(
                        "<p>", '<p style="padding: 0px; margin: 0px;">'
                    ),
                    "ships": [
                        [ship.name(), ship.type()]
                        for nickname, ship in faction.ships().items()
                    ],
                    "bases": [
                        [
                            base.name(),
                            base.owner().name(),
                            base.system_().name(),
                            base.system_().region(),
                        ]
                        for nickname, base in filter_oorp_bases(faction.bases()).items()
                    ],
                    "bribes": [
                        [
                            base.name(),
                            base.owner().name(),
                            base.system_().name(),
                            base.system_().region(),
                        ]
                        for nickname, base in faction.bribes().items()
                        if base.system_().nickname not in oorp
                    ],
                    "repsheet": reps,
                    "rumors": {
                        fl.bases[base].name(): text
                        for base, text in faction.rumors().items()
                    },
                    "time": datetime.now(tz=pytz.UTC).strftime(
                        "Page generated on the %d/%m/%Y at %H:%M:%S UTC"
                    ),
                }
        except TypeError:
            logging.exception(f"Error occured for faction {faction.nickname}: ")
    return factions


def get_commodities() -> dict:
    template = cv2.imread(r"hrc_template.png")

    def match_hrc_template(icon_path):
        method = cv2.TM_SQDIFF_NORMED
        icon = cv2.imread(icon_path)
        result = cv2.matchTemplate(template, icon, method)
        mn = cv2.minMaxLoc(result)[0]
        return mn < 0.1

    print("Reading commodity data...")
    commodities = {}
    for commodity in fl.commodities:
        if filter_oorp_bases(commodity.sold_at()).keys():
            try:
                try:
                    # save_icon(
                    #     icon=commodity.icon(),
                    #     name=commodity.nickname,
                    #     folder="commodities",
                    # )
                    hrc = True  # match_hrc_template(
                    #     f"../dumpedData/images/commodities/{commodity.nickname}.png"
                    # )
                except FileNotFoundError:
                    hrc = False

                commodities[commodity.nickname] = {
                    "name": commodity.name(),
                    "infocard": commodity.infocard(),
                    "volume": commodity.volume,
                    "decay": commodity.decay_per_second,
                    "defaultPrice": commodity.price(),
                    "hrc": hrc,
                    "boughtAt": [
                        [
                            base.name(),
                            base.owner().name(),
                            base.system_().name(),
                            base.system_().region(),
                            price,
                        ]
                        for base, price in filter_oorp_bases(
                            commodity.bought_at()
                        ).items()
                        if (hrc == True and commodity not in base.sells_commodities())
                        or (hrc == False)
                    ],
                    "soldAt": [
                        [
                            base.name(),
                            base.owner().name(),
                            base.system_().name(),
                            base.system_().region(),
                            price,
                        ]
                        for base, price in filter_oorp_bases(
                            commodity.sold_at()
                        ).items()
                    ],
                    "time": datetime.now(tz=pytz.UTC).strftime(
                        "This page was generated on the %d/%m/%Y at %H:%M:%S. Server-side data may be changed on the server at any time, without any notice to the user community. The only authoritative source for in-game data is the game itself."
                    ),
                }
            except TypeError:
                logging.exception(f"Error occured for commodity {commodity.nickname}")
    return commodities


def get_guns() -> dict:
    print("Reading weapon data...")

    guns = {}

    for gun in fl.routines.get_guns():
        try:
            sold_oorp_only = all(
                base.nickname in oorpBases for base in gun.sold_at().keys()
            )

            wrecks = []
            for wreck in {
                wreck
                for wreck in fl.routines.get_wrecks()
                if wreck.system().nickname not in oorp
            }:
                loot = [x[0] for x in wreck.loot()]
                if gun in loot:
                    wrecks.append(
                        [
                            wreck.name() if wreck.name() else "Unmarked Wreck",
                            wreck.system().name(),
                            wreck.sector(),
                        ]
                    )

            if (
                (gun.sold_at() and not sold_oorp_only) or wrecks or gun.name().isupper()
            ) and gun.is_valid():

                icon_name = iconname(gun.good().item_icon)

                # save_icon(icon=gun.icon(), name=icon_name, folder="guns")

                sold_at = {
                    base: price
                    for base, price in filter_oorp_bases(gun.sold_at()).items()
                }

                if gun.is_missile():
                    type = "missile"
                elif gun.is_turret():
                    type = "turret"
                else:
                    type = "gun"

                try:
                    range = round(gun.range(), 2)
                except ValueError:
                    range = 0

                guns[gun.nickname] = {
                    "name": gun.infocard("plain").split("\n")[0],
                    "shortName": gun.name(),
                    "icon_name": icon_name,
                    "infocard": gun.infocard(),
                    "hull_damage": round(gun.hull_damage(), 2),
                    "hull_dps": round(gun.hull_dps(), 2),
                    "shield_damage": round(gun.shield_damage(), 2),
                    "shield_dps": round(gun.shield_dps(), 2),
                    "refire": round(gun.refire(), 2),
                    "speed": gun.muzzle_velocity,
                    "energy_per_second": round(gun.energy_per_second(), 2),
                    "efficiency": round(gun.efficiency(), 2),
                    "refire_rate": round(gun.refire(), 2),
                    "rating": round(gun.rating(), 2),
                    "range": range,
                    "type": type,
                    "sold_at": list(
                        {
                            (
                                base.name(),
                                base.owner().name(),
                                base.system_().name(),
                                base.system_().region(),
                                price,
                            )
                            for base, price in sold_at.items()
                        }
                    ),
                    "wrecks": wrecks,
                    "time": datetime.now(tz=pytz.UTC).strftime(
                        "Page generated on the %d/%m/%Y at %H:%M:%S UTC"
                    ),
                }
        except:
            logging.exception(f"Error occured for gun {gun.nickname}: ")

    return dict(sorted(guns.items(), key=lambda x: bool(x[1]["sold_at"])))


def get_equipment() -> dict:
    print("Reading other equipment...")

    equipment = {
        "CounterMeasures": {},
        "Armor": {},
        "Cloaks": {},
        "Engines": {},
        "Shields": {},
        "Thrusters": {},
    }

    # CMs
    countermeasures = fl.equipment.of_type(flintClasses["CounterMeasureDropper"])
    for cm in countermeasures:
        flare = cm.countermeasure()
        if (
            not "_npc" in cm.nickname
            and not "npc_" in cm.nickname
            and flare.ammo_limit != inf
        ):
            # save_icon(
            #     icon=cm.icon(), name=iconname(cm.good().item_icon), folder="equipment"
            # )

            equipment["CounterMeasures"][cm.nickname] = {
                "name": cm.name(),
                "icon_name": iconname(cm.good().item_icon),
                "infocard": cm.infocard(),
                "price": cm.price(),
                "flare_price": flare.price(),
                "max_flares": flare.ammo_limit,
                "effectiveness": flare.effectiveness(),
                "range": flare.range,
                "lifetime": flare.lifetime,
                "availability": list(
                    {
                        (
                            base.name(),
                            base.owner().name(),
                            base.system_().name(),
                            base.system_().region(),
                            price,
                        )
                        for base, price in filter_oorp_bases(cm.sold_at()).items()
                    }
                ),
            }

    armors = fl.equipment.of_type(flintClasses["Armor"])
    for armor in armors:
        if filter_oorp_bases(armor.sold_at()):
            # save_icon(
            #     icon=armor.icon(),
            #     name=iconname(armor.good().item_icon),
            #     folder="equipment",
            # )

            equipment["Armor"][armor.nickname] = {
                "name": armor.name(),
                "icon_name": iconname(armor.good().item_icon),
                "infocard": armor.infocard(),
                "price": armor.price(),
                "volume": armor.volume,
                "multiplier": armor.hit_pts_scale,
                "availability": list(
                    {
                        (
                            base.name(),
                            base.owner().name(),
                            base.system_().name(),
                            base.system_().region(),
                            price,
                        )
                        for base, price in filter_oorp_bases(armor.sold_at()).items()
                    }
                ),
            }

    cloaks = fl.equipment.of_type(flintClasses["CloakingDevice"])
    for cloak in cloaks:
        if not cloak.name().isspace():
            # save_icon(
            #     icon=cloak.icon(),
            #     name=iconname(cloak.good().item_icon),
            #     folder="equipment",
            # )

            equipment["Cloaks"][cloak.nickname] = {
                "name": cloak.name(),
                "icon_name": iconname(cloak.good().item_icon),
                "infocard": cloak.infocard(),
                "price": cloak.price(),
                "volume": cloak.volume,
                "availability": list(
                    {
                        (
                            base.name(),
                            base.owner().name(),
                            base.system_().name(),
                            base.system_().region(),
                            price,
                        )
                        for base, price in filter_oorp_bases(cloak.sold_at()).items()
                    }
                ),
            }

    engines = fl.equipment.of_type(flintClasses["Engine"])
    for engine in engines:
        if filter_oorp_bases(engine.sold_at()):
            # save_icon(
            #     icon=engine.icon(),
            #     name=iconname(engine.good().item_icon),
            #     folder="equipment",
            # )

            equipment["Engines"][engine.nickname] = {
                "name": engine.name(),
                "icon_name": iconname(engine.good().item_icon),
                "infocard": engine.infocard(),
                "price": engine.price(),
                "cruise_speed": engine.cruise_speed_(),
                "cruise_charge_time": engine.cruise_charge_time,
                "availability": list(
                    {
                        (
                            base.name(),
                            base.owner().name(),
                            base.system_().name(),
                            base.system_().region(),
                            price,
                        )
                        for base, price in filter_oorp_bases(engine.sold_at()).items()
                    }
                ),
            }

    shields = fl.equipment.of_type(flintClasses["ShieldGenerator"])
    for shield in shields:
        if filter_oorp_bases(shield.sold_at()):
            # save_icon(
            #     icon=shield.icon(),
            #     name=iconname(shield.good().item_icon),
            #     folder="equipment",
            # )

            equipment["Shields"][shield.nickname] = {
                "name": shield.name(),
                "icon_name": iconname(shield.good().item_icon),
                "infocard": shield.infocard(),
                "price": shield.price(),
                "technology": shield.shield_type,
                "capacity": shield.max_capacity,
                "explosion_resistance": shield.explosion_resistance,
                "regen_rate": shield.regeneration_rate,
                "offline_rebuild_time": shield.offline_rebuild_time,
                "offline_threshold": shield.offline_threshold,
                "constant_power_draw": shield.constant_power_draw,
                "rebuild_power_draw": shield.rebuild_power_draw,
                "availability": list(
                    {
                        (
                            base.name(),
                            base.owner().name(),
                            base.system_().name(),
                            base.system_().region(),
                            price,
                        )
                        for base, price in filter_oorp_bases(shield.sold_at()).items()
                    }
                ),
            }

    thrusters = fl.equipment.of_type(flintClasses["Thruster"])
    for thruster in thrusters:
        if filter_oorp_bases(thruster.sold_at()):
            # save_icon(
            #     icon=thruster.icon(),
            #     name=iconname(thruster.good().item_icon),
            #     folder="equipment",
            # )

            equipment["Thrusters"][thruster.nickname] = {
                "name": thruster.name(),
                "icon_name": iconname(thruster.good().item_icon),
                "infocard": thruster.infocard(),
                "price": thruster.price(),
                "power_usage": thruster.power_usage,
                "max_force": thruster.max_force,
                "efficiency": thruster.efficiency(),
                "explosion_resistance": thruster.explosion_resistance,
                "availability": list(
                    {
                        (
                            base.name(),
                            base.owner().name(),
                            base.system_().name(),
                            base.system_().region(),
                            price,
                        )
                        for base, price in filter_oorp_bases(thruster.sold_at()).items()
                    }
                ),
            }

    equipment["CounterMeasures"] = dict(
        sorted(
            equipment["CounterMeasures"].items(),
            key=lambda x: bool(x[1]["availability"]),
        )
    )
    equipment["Cloaks"] = dict(
        sorted(equipment["Cloaks"].items(), key=lambda x: bool(x[1]["availability"]))
    )
    return equipment


def main(dumpModels: bool):
    with open("secret.json", "r") as f:
        cconfig = load(f)
    fl.set_install_path(cconfig["freelancerPath"])

    apply_server_infocard_override()

    global oorpBases
    oorpBases = [b.nickname for b in fl.bases if b.system_().nickname in oorp]
    global infocardMap
    infocardMap = fl.interface.get_infocardmap()
    global commodity_table
    commodity_table = {
        commodity.nickname: commodity.name() for commodity in fl.commodities
    }
    data = {
        "README": f"This file was automatically generated by {basename(__file__)}. Do not edit unless you know what you're doing!",
        "Version": version,
        "Ships": get_ships(definitions=tech.get_definitions(), dumpModels=dumpModels),
        "Systems": get_systems(get_system_images=config["wikiGen"]["dumpSysmaps"]),
        "Bases": get_bases(),
        "Factions": get_factions(),
        "Commodities": get_commodities(),
        "Weapons": get_guns(),
        "Equipment": get_equipment(),
    }

    if len(processes) > 0:
        for process in processes:
            process.wait()
    return data


if __name__ == "__main__":
    try:
        if fl.paths.is_probably_freelancer(argv[1]):
            fl.set_install_path(argv[1])
        else:
            print("Invalid directory")
            quit()
    except IndexError:
        print(
            f"Path to Freelancer directory not given.\nUsage: python {basename(__file__)} [path_to_freelancer]"
        )
        fl.set_install_path(input())

    oorpBases = [b.nickname for b in fl.bases if b.system_().nickname in oorp]
    infocardMap = fl.interface.get_infocardmap()
    commodity_table = {
        commodity.nickname: commodity.name() for commodity in fl.commodities
    }

    filename = "flData.json"
    print("Dumping game data\n===================")
    startTime = perf_counter()
    data = {
        "README": f"This file was automatically generated by {basename(__file__)}. Do not edit unless you know what you're doing!",
        "Version": version,
        "Ships": get_ships(definitions=tech.get_definitions(), dumpModels=False),
        "Systems": get_systems(get_system_images=config["wikiGen"]["dumpSysmaps"]),
        "Bases": get_bases(),
        "Factions": get_factions(),
        "Commodities": get_commodities(),
        "Weapons": get_guns(),
        "Equipment": get_equipment(),
    }
    print(f"Game files read, writing {filename}...")
    with open(f"../dumpedData/{filename}", "w") as f:
        dump(data, f, indent=1)
    endTime = perf_counter()
    print(f"Done.\nReading and writing took {round(endTime-startTime, 2)}s")
