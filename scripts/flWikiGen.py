import flint as fl
import discoTechCompat as tech
from json import dump
from time import time
from math import pi
from sys import argv
from os import path, getcwd
from os.path import exists
try:
    if path.exists(argv[1]):
        if exists(argv[1] + "\\EXE\\freelancer.exe"):
            fl.set_install_path(argv[1])
    else:
        print("Invalid directory")
        quit()
except IndexError:
    print(f"Path to Freelancer directory not given.\nUsage: python {path.basename(__file__)} [path_to_freelancer]")
    quit()

# LOOKUP TABLES
gun_table = {}
for x in fl.equipment:
    try:
        if str(type(x)) == "<class 'flint.entities.equipment.Gun'>" and x.is_valid():
            gun_table[x.nickname] = x.name()
    except:
        pass

base_table = {}
for base in fl.bases:
    if base.has_solar():
        try:
            base_table[base.nickname] = base.name()
        except TypeError:
            pass

def degree(x):
    degree = (x * 180) / pi
    return degree

def linear_search(array, to_find):
	for i in range(0, len(array)):
		if array[i] == to_find:
			return True
	return False

def reverse_dict(myDict):
    reversedDict = {}
    for key in myDict:
        val = myDict[key]
        reversedDict[val] = key
    return reversedDict

def get_ships(definitions) -> dict:
    print("Reading ship data...")
    ships = {}
    for ship in fl.ships:
        if not "_npc" in ship.nickname and ship.sold_at():
            try:
                if "li_" in ship.nickname:
                    built_by = "Liberty"
                elif "br_" in ship.nickname:
                    built_by = "Bretonia"
                elif "ku_" in ship.nickname:
                    built_by = "Kusari"           
                elif "rh_" in ship.nickname:
                    built_by = "Rheinland"
                elif "ga_" in ship.nickname:
                    built_by = "Gallia"
                elif "bw_" in ship.nickname:
                    built_by = "Borderworlds"
                elif "co_" in ship.nickname:
                    built_by = "Corsairs"
                elif "oc_" in ship.nickname:
                    built_by = "Outcasts"
                elif "col_" in ship.nickname:
                    built_by = "Crayter Republic"
                elif "or_" in ship.nickname:
                    built_by = "The Order"
                else:
                    built_by = ""

                sold_at = []
                for x in ship.sold_at():
                    if x.has_solar():
                        sold_at.append([x.name(), x.owner().name(), x.system_().name(), x.system_().region()])

                equipment = []
                for x in ship.equipment():
                    equipment.append([f"* [[{x.name()}]]", x.price()])

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
                    if hardpoints.count(x) > 1:
                        tempHardpoints.append(f"*{hardpoints.count(x)}x [[{x}]]")
                    else:
                        tempHardpoints.append(f"* [[{x}]]")
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
                maxThrust = int(force / linear_drag) if thrusterCount > 0 else ""

                mustUseMoors = False if ship.mission_property == 'can_use_berths' else True

                infocard = ship.infocard('plain').split("<p>")[0]
                ships[ship.name()] = {"nickname" : ship.nickname, "longName" : ship.infocard('plain').split("\n")[0], "maneuverability" : infocardMan,"techcompat": techcompat, "type" : ship.type(), "maxClass" : maxClass, "maxShield" : maxShield, "infocard" : infocard, "hull_price" : hull_price, "package_price" : ship.price(), "impulse_speed" : int(ship.impulse_speed()), "maxThrust" : maxThrust, "hit_pts" : ship.hit_pts, "hold_size" : ship.hold_size, "gunCount" : gunCount, "thrusterCount" : thrusterCount, "turretCount" : turretCount, "torpedoCount" : torpedoCount, "mineCount" : mineCount, "cmCount" : cmCount, "bot_limit" : ship.nanobot_limit, "bat_limit" : ship.shield_battery_limit, "power_output" : power_output, "maxCruise" : ship.engine().cruise_speed if ship.engine().cruise_speed != 0 else 350, "power_recharge" : power_recharge,"turnRate" : round(turnRate, 2), "angularDistance0.5" : angularDistanceInTime, "responseTime" : responseTime, "built_by" : built_by, "mustUseMoors" : mustUseMoors, "equipment" : equipment, "sold_at" : sold_at, "hardpoints" : hardpoints}
            except TypeError:
                pass
    return ships

def get_bases() -> dict:
    print("Reading base data...")
    bases = {}
    for base in fl.bases:
        if True:#base.has_solar():
            try:
                ships_sold = []
                for x in base.sells_ships():
                    ships_sold.append(x.name())
                bases[base.name()] = {"infocard" : base.infocard('html'), "owner" : base.owner().name(), "system" : base.system_().name(), "sector" : base.sector(), "ships_sold" : ships_sold}
            except (TypeError, AttributeError):
                pass
    return bases

def get_systems() -> dict:
    print("Reading system data...")
    systems = {}
    for system in fl.systems:
        bases = []
        connections = []
        zones = []
        for x in system.bases():
            bases.append(x.name())
        for x in system.connections():
            if not "->" in x.name():
                connections.append(x.name())
            else:
                index = x.name().find('>') + 2
                name = x.name()[index:]
                connections.append(f"{name} Jump Gate")
        for x in system.zones():
            zones.append(x.name())
        zones = list( dict.fromkeys(zones) )            #   remove duplicates
        connections = list( dict.fromkeys(connections) )#

        systems[system.name()] = {"nickname" : system.nickname, "infocard" : system.infocard(), "infocard_plain" : system.infocard(markup = 'plain'), "region" : system.region(), "bases" : bases, "connections" : connections, "zones" : zones}
    return systems

def get_commodities() -> dict:
    print("Reading commodity data...")
    commodities = {}
    for commodity in fl.equipment:
        try:
            if str(type(commodity)) == "<class 'flint.entities.equipment.Commodity'>":
                boughtAt = {}
                for base in commodity.bought_at().items():
                    boughtAt[base[0].name()] = base[1]
                commodities[commodity.name()] = {"nickname" : commodity.nickname, "infocard" : commodity.infocard(), "infocard_plain" : commodity.infocard(markup = 'plain'), "price" : commodity.price(), "bought_at" : boughtAt}
        except:
            pass
    return commodities

def get_guns() -> dict:
    print("Reading weapon data...")
    guns = {}
    for gun in fl.equipment:
        try:
            if str(type(gun)) == "<class 'flint.entities.equipment.Gun'>" and gun.is_valid():
                Value = gun.hull_dps() / gun.price() * 1000 if gun.hull_dps() > gun.shield_dps() else gun.shield_dps() / gun.price() * 1000
                Rating = gun.efficiency() * Value
                if gun.is_missile():
                    type = "missile"
                elif gun.is_turret():
                    type = "turret"
                else:
                    type = "gun"
                guns[gun.name()] = {"nickname" : gun.nickname ,"infocard" : gun.infocard(),"price" : gun.price() ,"type" : type, "technology" : gun.technology(), "hull_damage" : gun.hull_damage(), "shield_damage" : gun.shield_damage(), "hull_damage/s" : round(gun.hull_dps(),2), "shield_damage/s" : round(gun.shield_dps(),2),"power_usage" : gun.power_usage,"power_usage/s" : round(gun.energy_per_second(), 2), "efficiency" : round(gun.efficiency(), 4),"refire_rate" : round(gun.refire(), 2), "range" : gun.range(),"projectile_speed" : gun.muzzle_velocity, "value" : round(Value,2), "rating" : round(Rating,2), "lootable" : gun.lootable}
        except AttributeError:
            pass

    gunsSold = []
    gunsSoldAt = {}
    for base in fl.bases:
        for gun in base.sells_equipment():
            try:
                if str(type(gun)) == "<class 'flint.entities.equipment.Gun'>" and gun.is_valid():
                    gunsSold.append(gun.name())
            except:
                pass
        gunsSoldAt[base.name()] = gunsSold
        gunsSold = []

    temp = {}
    list = []
    deleteLater = []
    for gun in guns:
        for x in gunsSoldAt.items():
            if linear_search(x[1], gun):
                base = x[0]
                # skip = False
                # try:
                #     system = fl.bases[reverse_dict(base_table)[base]].system_().name()
                # except (AttributeError, KeyError):
                #     skip = True
                # try:
                #     sector = fl.bases[reverse_dict(base_table)[base]].sector()
                # except (AttributeError, KeyError):
                #     skip = True
                # try:
                #     faction = fl.bases[reverse_dict(base_table)[base]].owner().name()
                # except (AttributeError, KeyError):
                #     skip = True
                list.append([base])
        try:
            temp[gun] = list[0]
        except:
            temp[gun] = []
            deleteLater.append(gun)
        list = []

    for x in guns.items():
        x[1]["sold_at"] = temp[x[0]]
    for x in deleteLater:
        del guns[x]
    return guns

filename = "flData.json"
print("Reading game files...")
startTime = time()
data = {"README" : f"This file was automatically generated by {path.basename(__file__)}. Do not edit unless you know what you're doing!",
        "Ships" : get_ships(tech.get_definitions())}
#midTime = time()
print(f"Game files read, writing {filename}...")
with open(f'{getcwd()}\\{filename}', 'w') as f:
    dump(data, f, indent=1)
endTime = time()
print(f"Done.\nReading and writing took {round(endTime-startTime, 2)}s")