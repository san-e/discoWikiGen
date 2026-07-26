from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

import flint as fl

# import discoTechCompat as tech # disable this because the techcompat site is behind cloudflare now
from json import load

from math import pi, inf
from os import makedirs
from os.path import exists, basename, splitext
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import cv2
import subprocess
import time

import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

version = ""  # input("Enter game version: ")

with open("./config.json", "r") as file:
    config = load(file)
with open("./secret.json", "r") as file:
    secrets = load(file)
LLEDITSCRIPT = (
        secrets["librelancer"] + f"/lleditscript{'.exe' if os.name == 'nt' else ''}"
)
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


def filter_oorp_bases(
        bases,
) -> list[fl.entities.Base] | dict | EntitySet[fl.entities.Base]:
    if not bases:
        return {}
    if type(bases) == list:
        return list(filter(lambda x: x.nickname not in oorpBases, bases))
    elif type(bases) == dict:
        return dict(filter(lambda x: x[0].nickname not in oorpBases, bases.items()))
    elif type(bases) == EntitySet:
        return EntitySet(filter(lambda x: x.nickname not in oorpBases, bases.values()))
    raise ValueError("bases is of incompatible type " + type(bases))


processes = set()
MAX_PROCESSES = 50


def dump_model(model, materials, destination) -> None:
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


def iconname(path) -> str:
    return splitext(basename(path))[0]


# ------------------------------------------------ #


def get_ships(definitions: dict, dumpModels: bool) -> dict[str, ShipEntry]:
    print("Reading ship data...")
    ships = {}
    for ship in fl.ships:
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

            equipment = {}
            for x in ship.equipment():
                equipment[x.name()] = x.price()

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

            hardpoints = defaultdict(int)
            for x in ship.hardpoints().values():
                if x[0].name() != x[0].nickname:
                    hardpoints[x[0].name()] += 1

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

            ships[ship.nickname] = ShipEntry(
                ship.name(),
                ship.infocard("plain").split("\n")[0],
                components,
                infocardMan,
                built_by,
                techcompat,
                ship.type(),
                maxClass,
                maxShield,
                infocard.replace("&nbsp;", ""),
                hull_price,
                ship.price(),
                int(ship.impulse_speed()),
                maxThrust,
                ship.hit_pts,
                ship.hold_size,
                gunCount,
                thrusterCount,
                turretCount,
                torpedoCount,
                mineCount,
                cmCount,
                ship.nanobot_limit,
                ship.shield_battery_limit,
                power_output,
                maxCruise,
                power_recharge,
                round(turnRate, 2),
                angularDistanceInTime,
                responseTime,
                mustUseMoors,
                equipment,
                {
                    base.nickname
                    for base in filter_oorp_bases(ship.sold_at())
                    if base.has_solar()
                },
                hardpoints,
            )

        except TypeError as e:
            print(f"Error occured for ship {ship.nickname}")
            raise e
    return ships


def get_bases() -> dict[str, BaseEntry]:
    print("Reading base data...")
    bases = {}
    for base in fl.bases:
        if not base.has_solar() or base.nickname in oorpBases:
            continue
        try:
            bases[base.nickname] = BaseEntry.from_nickname(base.nickname)
        except (TypeError, AttributeError) as e:
            print(f"Error occured for base {base.nickname}")
            raise e
    return bases


def get_systems(get_system_images=False) -> dict[str, SystemEntry]:
    print("Reading system data...")

    # Selenium setup
    if get_system_images:
        options = Options()
        options.binary_location = r"/usr/bin/firefox"
        options.add_argument("-headless")
        options.set_preference("layout.css.devPixelsPerPx", "2.0")
        driver = webdriver.Firefox(options=options)
        driver.set_window_size(1920, 1080)
        driver.get(config["wikiGen"]["sysmapURL"])

    systems = {}
    for system in fl.systems:
        try:
            if system.nickname not in oorp:
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
                            x.infocard("html"),
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
                    time.sleep(1)
                    x = 0
                    while (
                            driver.find_elements(By.CLASS_NAME, "loadingOverlay")
                            or driver.find_elements(By.CLASS_NAME, "loaderTitle")
                            or driver.find_elements(By.CLASS_NAME, "systemTitle")[0]
                            == "Sirius"
                    ):
                        time.sleep(0.1)
                        x += 1
                        if x >= 100:
                            driver.execute_script("location.reload(true);")
                            x = 0
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

                systems[system.nickname] = SystemEntry(
                    system.name(),
                    system.infocard("plain"),
                    (
                        system.region()
                        if system.region() != "Independent"
                        else "Independent Worlds"
                    ),
                    {base.nickname for base in system.bases()},
                    planets,
                    stars,
                    holes,
                    neighbors,
                    zones,
                    nebulae,
                    asteroids,
                    wrecks,
                )

        except Exception as e:
            print(f"Error occurred for system {system.nickname}")
            raise e
    if get_system_images:
        driver.quit()
    return systems


def get_factions() -> dict[str, FactionEntry]:
    print("Reading faction data...")
    factions = {}
    for faction in fl.factions:
        try:
            if faction.nickname not in faction.name() and not faction.name().isspace():
                factions[faction.nickname] = FactionEntry.from_nickname(faction.nickname)
        except TypeError as e:
            print(f"Error occurred for faction {faction.nickname}")
            raise e
    return factions


def get_commodities() -> dict[str, CommodityEntry]:
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
                commodities[commodity.nickname] = CommodityEntry.from_nickname(commodity.nickname)
            except TypeError as e:
                print(f"Error occurred for commodity {commodity.nickname}")
                raise e
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
                guns[gun.nickname] = GunEntry.from_nickname(gun.nickname)
        except Exception as e:
            print(f"Error occurred for gun {gun.nickname}")
            raise e

    return dict(sorted(guns.items(), key=lambda x: bool(x[1]["sold_at"])))

def get_countermeasures() -> dict[str, CountermeasureEntry]:
    cms = {}
    countermeasures = fl.equipment.of_type(flintClasses["CounterMeasureDropper"])
    for cm in countermeasures:
        flare = cm.countermeasure()
        if (
                not "_npc" in cm.nickname
                and not "npc_" in cm.nickname
                and flare.ammo_limit != inf
                and cm.good()
        ):
            # save_icon(
            #     icon=cm.icon(), name=iconname(cm.good().item_icon), folder="equipment"
            # )

            cms[cm.nickname] = CountermeasureEntry.from_nickname(cm.nickname)
    return cms

def get_armors() -> dict[str, ArmorEntry]:
    armor = {}
    armors = fl.equipment.of_type(flintClasses["Armor"])
    for armor in armors:
        if filter_oorp_bases(armor.sold_at()):
            # save_icon(
            #     icon=armor.icon(),
            #     name=iconname(armor.good().item_icon),
            #     folder="equipment",
            # )

            armor[armor.nickname] = ArmorEntry.from_nickname(armor.nickname)
    return armor

def get_cloaks() -> dict[str, CloakEntry]:
    c = {}
    cloaks = fl.equipment.of_type(flintClasses["CloakingDevice"])
    for cloak in cloaks:
        if not cloak.name().isspace():
            # save_icon(
            #     icon=cloak.icon(),
            #     name=iconname(cloak.good().item_icon),
            #     folder="equipment",
            # )

            c[cloak.nickname] = CloakEntry.from_nickname(cloak.nickname)
    return c

def get_engines() -> dict[str, EngineEntry]:
    e = {}
    engines = fl.equipment.of_type(flintClasses["Engine"])
    for engine in engines:
        if filter_oorp_bases(engine.sold_at()):
            # save_icon(
            #     icon=engine.icon(),
            #     name=iconname(engine.good().item_icon),
            #     folder="equipment",
            # )

            e[engine.nickname] = EngineEntry.from_nickname(engine.nickname)
    return e

def get_shields() -> dict[str, ShieldEntry]:
    s = {}
    shields = fl.equipment.of_type(flintClasses["ShieldGenerator"])
    for shield in shields:
        if filter_oorp_bases(shield.sold_at()):
            # save_icon(
            #     icon=shield.icon(),
            #     name=iconname(shield.good().item_icon),
            #     folder="equipment",
            # )

            s[shield.nickname] = ShieldEntry.from_nickname(shield.nickname)
    return s

def get_thrusters() -> dict[str, ThrusterEntry]:
    t = {}
    thrusters = fl.equipment.of_type(flintClasses["Thruster"])
    for thruster in thrusters:
        if filter_oorp_bases(thruster.sold_at()):
            # save_icon(
            #     icon=thruster.icon(),
            #     name=iconname(thruster.good().item_icon),
            #     folder="equipment",
            # )

            t[thruster.nickname] = ThrusterEntry.from_nickname(thruster.nickname)
    return t


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
    data = CompoundEntries(
        get_ships(definitions={}, dumpModels=dumpModels),
        get_systems(get_system_images=config["wikiGen"]["dumpSysmaps"]),
        get_bases(),
        get_factions(),
        get_commodities(),
        get_guns(),
        get_countermeasures(),
        get_armors(),
        get_cloaks(),
        get_engines(),
        get_shields(),
        get_thrusters()
    )

    if len(processes) > 0:
        for process in processes:
            process.wait()
    return data


@dataclass(eq=True, unsafe_hash=True)
class CompoundEntries:
    ships: dict[str, ShipEntry]
    systems: dict[str, SystemEntry]
    bases: dict[str, BaseEntry]
    factions: dict[str, FactionEntry]
    commodities: dict[str, CommodityEntry]
    guns: dict[str, GunEntry]
    countermeasures: dict[str, CountermeasureEntry]
    armors: dict[str, ArmorEntry]
    cloaks: dict[str, CloakEntry]
    engines: dict[str, EngineEntry]
    shields: dict[str, ShieldEntry]
    thrusters: dict[str, ThrusterEntry]

    def __post_init__(self):
        self.link()

        self.countermeasures = dict(
            sorted(
                self.countermeasures.items(),
                key=lambda x: bool(x[1].availability),
            )
        )

        self.cloaks = dict(
            sorted(self.cloaks.items(), key=lambda x: bool(x[1].availability))
        )

    def link(self):
        for entry in self.ships.values():
            for nick in entry._sold_at_ids:
                entry.sold_at.add(self.bases[nick])

        for entry in self.systems.values():
            for nick in entry._bases_ids:
                entry.bases.add(self.bases[nick])
            for nick in entry._neighbors_ids:
                entry.neighbors.add(self.systems[nick])

        for entry in self.bases.values():
            for nick in entry._ships_sold_ids:
                entry.ships_sold.add(self.ships[nick])

        for entry in self.factions.values():
            for nick in entry._ships_ids:
                entry.ships.add(self.ships[nick])
            for nick in entry._bases_ids:
                entry.bases.add(self.bases[nick])
            for nick in entry._bribes_ids:
                entry.bribes.add(self.factions[nick])
            for nick, value in entry._repsheet_ids.items():
                entry.repsheet[self.factions[nick]] = value
            for nick, rumor in entry._rumors_ids.items():
                entry.rumors[self.factions[nick]] = rumor

        for entry in self.commodities.values():
            for nick in entry._boughtAt_ids:
                entry.boughtAt.add(self.bases[nick])
            for nick in entry._soldAt_ids:
                entry.soldAt.add(self.bases[nick])

        for entry in self.guns.values():
            for nick in entry._availability_ids:
                entry.availability.add(self.bases[nick])
        for entry in self.countermeasures.values():
            for nick in entry._availability_ids:
                entry.availability.add(self.bases[nick])
        for entry in self.armors.values():
            for nick in entry._availability_ids:
                entry.availability.add(self.bases[nick])
        for entry in self.cloaks.values():
            for nick in entry._availability_ids:
                entry.availability.add(self.bases[nick])
        for entry in self.engines.values():
            for nick in entry._availability_ids:
                entry.availability.add(self.bases[nick])
        for entry in self.shields.values():
            for nick in entry._availability_ids:
                entry.availability.add(self.bases[nick])
        for entry in self.thrusters.values():
            for nick in entry._availability_ids:
                entry.availability.add(self.bases[nick])


@dataclass(eq=True, unsafe_hash=True)
class ShipEntry:
    name: str
    longName: str
    components: dict[str, str]
    maneuverability: str
    built_by: str
    techcompat: str
    type: str
    maxClass: int
    maxShield: int
    infocard: str
    hull_price: int
    package_price: int
    impulse_speed: int
    maxThrust: int
    hit_pts: int
    hold_size: int
    gunCount: int
    thrusterCount: int
    turretCount: int
    torpedoCount: int
    mineCount: int
    cmCount: int
    bot_limit: int
    bat_limit: int
    power_output: int
    maxCruise: int
    power_recharge: int
    turnRate: float
    angularDistance: float
    responseTime: float
    mustUseMoors: bool
    equipment: dict[str, int]
    _sold_at_ids: set[str]
    sold_at: set[BaseEntry] = field(default_factory=set, init=False)
    hardpoints: dict[str, int]


@dataclass(eq=True, unsafe_hash=True)
class SystemEntry:
    name: str
    infocard: str
    region: str
    _bases_ids: set[str]
    bases: set[BaseEntry] = field(default_factory=set, init=False)
    planets: list[list[str]]
    stars: dict[str, str]
    holes: list[list[str]]
    _neighbors_ids: list[str]
    neighbors: set[SystemEntry] = field(default_factory=set, init=False)
    zones: list[list[str]]
    nebulae: list[list[str]]
    asteroids: list[list[str]]
    wrecks: list[dict[str, str | list[str | int]]]


@dataclass(eq=True, unsafe_hash=True)
class BaseEntry:
    name: str
    infocard: str
    owner: str
    system: str
    region: str
    sector: str
    bribes: list[str]
    missions: list[str]
    rumors: dict[str, set[str]]
    news: dict[str, str]
    commodities_buying: dict[str, int]
    commodities_selling: dict[str, int]
    equipment_selling: dict[str, int]
    _ships_sold_ids: set[str]
    ships_sold: set[ShipEntry] = field(default_factory=set, init=False)
    type: str

    @classmethod
    def from_nickname(cls, nickname: str) -> BaseEntry:
        base = fl.get_bases()[nickname]
        return cls(
            base.name(),
            base.infocard(),
            base.owner(),
            base.system_(),
            base.system_().region(),
            base.sector(),
            [faction.name() for faction in base.bribes()],
            [faction.name() for faction in base.missions()],
            {faction.name(): rumor for faction, rumor in base.rumors().items()},
            {newsitem.headline_(): newsitem.text_() for newsitem in base.news()},
            {
                commodity.nickname: cost
                for commodity, cost in base.buys_commodities().items()
            },
            {
                commodity.nickname: cost
                for commodity, cost in base.sells_commodities().items()
            },
            {
                equipment.nickname: cost
                for equipment, cost in base.sells_equipment().items()
            },
            {ship.nickname for ship, price in base.sells_ships().items()},
            str(type(base)),
        )


@dataclass(eq=True, unsafe_hash=True)
class FactionEntry:
    name: str
    shortName: str
    alignment: str
    infocard: str
    _ships_ids: set[str]
    ships: set[ShipEntry] = field(default_factory=set, init=False)
    _bases_ids: list[str]
    bases: set[BaseEntry] = field(default_factory=set, init=False)
    _bribes_ids: set[str]
    bribes: set[FactionEntry] = field(default_factory=set, init=False)
    _repsheet_ids: dict[str, float]
    repsheet: dict[FactionEntry, float] = field(default_factory=dict, init=False)
    _rumors_ids: dict[str, str]
    rumors: dict[FactionEntry, str] = field(default_factory=dict, init=False)
    legality: str

    @classmethod
    def from_nickname(cls, nickname: str) -> FactionEntry:
        faction = fl.get_factions()[nickname]
        return cls(
            faction.name(),
            faction.short_name(),
            (
                "Corporation"
                if faction.name() in config["pageGen"]["corporations"]
                else faction.legality()
            ),
            faction.infocard(),
            {nickname for nickname, ship in faction.ships().items()},
            list(filter_oorp_bases(faction.bases()).keys()),
            set(filter_oorp_bases(faction.bribes()).keys()),
            dict(sorted({
                faction.name(): rep
                for faction, rep in faction.rep_sheet().items()
                if rep
            }, key=lambda x: x[1])),
            {base.name(): text for base, text in faction.rumors().items()},
            faction.legality(),
        )


@dataclass(eq=True, unsafe_hash=True)
class CommodityEntry:
    name: str
    infocard: str
    volume: int
    decay: int
    defaultPrice: int
    hrc: bool
    _boughtAt_ids: set[str]
    boughtAt: set[BaseEntry] = field(default_factory=set, init=False)
    _soldAt_ids: set[str]
    soldAt: set[BaseEntry] = field(default_factory=set, init=False)

    @classmethod
    def from_nickname(cls, nickname: str) -> CommodityEntry:
        commodity = fl.get_commodities()[nickname]
        hrc = False
        return cls(
            commodity.name(),
            commodity.infocard(),
            commodity.volume,
            commodity.decay_per_second,
            commodity.price(),
            hrc,
            {
                base.nickname
                for base, price in filter_oorp_bases(
                commodity.bought_at()
            ).items()
                if (hrc == True and commodity not in base.sells_commodities())
                   or (hrc == False)
            },
            {
                base.nickname
                for base, price in filter_oorp_bases(
                commodity.sold_at()
            ).items()
            },
        )


@dataclass(eq=True, unsafe_hash=True)
class EquipmentEntry:
    name: str
    icon_name: str
    infocard: str
    _availability_ids: set[str]
    availability: set[BaseEntry] = field(default_factory=set, init=False)


@dataclass(eq=True, unsafe_hash=True)
class GunEntry(EquipmentEntry):
    shortName: str
    hull_damage: float
    hull_dps: float
    shield_damage: float
    shield_dps: float
    refire: float
    speed: int
    energy_per_second: float
    efficiency: float
    rating: float
    range: int
    type: str
    wrecks: list[list[str]]

    @classmethod
    def from_nickname(cls, nickname: str) -> GunEntry:
        gun = fl.get_guns()[nickname]
        return cls(
            gun.infocard("plain").split("\n")[0],
            iconname(gun.good().item_icon),
            gun.infocard(),
            gun.name(),
            {base.nickname for base, price in gun.sold_at().items()},
            round(gun.hull_damage(), 2),
            round(gun.hull_dps(), 2),
            round(gun.shield_damage(), 2),
            round(gun.shield_dps(), 2),
            round(gun.refire(), 2),
            gun.muzzle_velocity,
            round(gun.energy_per_second(), 2),
            round(gun.efficiency(), 2),
            round(gun.rating(), 2),
            round(gun.range(), 2),
            "missile" if gun.is_missile() else ("turret" if gun.is_turret() else "gun"),
            [
                [
                    wreck.name() if wreck.name() else "Unmarked Wreck",
                    wreck.system().name(),
                    wreck.sector(),
                ]
                for wreck in fl.routines.get_wrecks()
                if wreck.system().nickname not in oorp
                   and gun in [x[0] for x in wreck.loot()]
            ],
        )


@dataclass(eq=True, unsafe_hash=True)
class CountermeasureEntry(EquipmentEntry):
    price: int
    flare_price: int
    max_flares: int
    effectiveness: float
    range: float
    lifetime: float

    @classmethod
    def from_nickname(cls, nickname: str) -> CountermeasureEntry:
        cm: fl.entities.equipment.CounterMeasureDropper = \
        fl.get_equipment().of_type(fl.entities.equipment.CounterMeasureDropper)[nickname]
        flare = cm.countermeasure()
        return cls(
            cm.name(),
            iconname(cm.good().item_icon),
            cm.infocard(),
            {
                base.nickname
                for base, price in filter_oorp_bases(cm.sold_at()).items()
            },
            cm.price(),
            flare.price(),
            flare.ammo_limit,
            flare.effectiveness(),
            flare.range,
            flare.lifetime,
        )


@dataclass(eq=True, unsafe_hash=True)
class ArmorEntry(EquipmentEntry):
    price: int
    volume: int
    multiplier: float

    @classmethod
    def from_nickname(cls, nickname: str) -> ArmorEntry:
        armor: fl.entities.equipment.Armor = \
            fl.get_equipment().of_type(fl.entities.equipment.Armor)[nickname]
        return cls(
            armor.name(),
            iconname(armor.good().item_icon),
            armor.infocard(),
            {
                base.nickname
                for base, price in filter_oorp_bases(armor.sold_at()).items()
            },
            armor.price(),
            armor.volume,
            armor.hit_pts_scale
        )

@dataclass(eq=True, unsafe_hash=True)
class CloakEntry(EquipmentEntry):
    price: int
    volume: int

    @classmethod
    def from_nickname(cls, nickname: str) -> CloakEntry:
        cloak: fl.entities.equipment.CloakingDevice = \
            fl.get_equipment().of_type(fl.entities.equipment.CloakingDevice)[nickname]
        return cls(
            cloak.name(),
            iconname(cloak.good().item_icon),
            cloak.infocard(),
            {
                base.nickname
                for base, price in filter_oorp_bases(cloak.sold_at()).items()
            },
            cloak.price(),
            cloak.volume,
        )


@dataclass(eq=True, unsafe_hash=True)
class EngineEntry(EquipmentEntry):
    price: int
    cruise_speed: float
    cruise_charge_time: int

    @classmethod
    def from_nickname(cls, nickname: str) -> EngineEntry:
        engine: fl.entities.equipment.Engine = \
            fl.get_equipment().of_type(fl.entities.equipment.Engine)[nickname]
        return cls(
            engine.name(),
            iconname(engine.good().item_icon),
            engine.infocard(),
            {
                base.nickname
                for base, price in filter_oorp_bases(engine.sold_at()).items()
            },
            engine.price(),
            engine.cruise_speed,
            engine.cruise_charge_time,
        )


@dataclass(eq=True, unsafe_hash=True)
class ShieldEntry(EquipmentEntry):
    price: int
    technology: str
    capacity: float
    explosion_resistance: float
    regen_rate: float
    offline_rebuild_time: float
    offline_threshold: float
    constant_power_draw: float
    rebuild_power_draw: float

    @classmethod
    def from_nickname(cls, nickname: str) -> ShieldEntry:
        shield: fl.entities.equipment.ShieldGenerator = \
            fl.get_equipment().of_type(fl.entities.equipment.ShieldGenerator)[nickname]
        return cls(
            shield.name(),
            iconname(shield.good().item_icon),
            shield.infocard(),
            {
                base.nickname
                for base, price in filter_oorp_bases(shield.sold_at()).items()
            },
            shield.shield_type,
            shield.max_capacity if shield.max_capacity else 0,
            (shield.explosion_resistance if shield.explosion_resistance else 0),
            (shield.regeneration_rate if shield.regeneration_rate else 0),
            (shield.offline_rebuild_time if shield.offline_rebuild_time else 0),
            (shield.offline_threshold if shield.offline_threshold else 0),
            (shield.constant_power_draw if shield.constant_power_draw else 0),
            (shield.rebuild_power_draw if shield.rebuild_power_draw else 0),

        )


@dataclass(eq=True, unsafe_hash=True)
class ThrusterEntry(EquipmentEntry):
    price: int
    power_usage: float
    max_force: float
    efficiency: float
    explosion_resistance: float

    @classmethod
    def from_nickname(cls, nickname: str) -> ThrusterEntry:
        thruster: fl.entities.equipment.Thruster = \
            fl.get_equipment().of_type(fl.entities.equipment.Thruster)[nickname]
        return cls(
            thruster.name(),
            iconname(thruster.good().item_icon),
            thruster.infocard(),
            {
                base.nickname
                for base, price in filter_oorp_bases(thruster.sold_at()).items()
            },
            thruster.price(),
            thruster.power_usage,
            thruster.max_force,
            thruster.efficiency(),
            thruster.explosion_resistance,
        )

