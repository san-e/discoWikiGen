import flint as fl
import json
import time
from os import path
fl.set_install_path("A:\Spiele\Freelancer\Discovery Freelancer")
#fl.set_install_path("A:\Spiele\Freelancer\Discovery Freelancer the second")

# LOOKUP TABLES
gun_table = {}
for x in fl.equipment:
    try:
        if x.classIsGun and x.is_valid():
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

def get_ships() -> dict:
    print("Reading ship data...")
    ships = {}
    for ship in fl.ships:
        if not "_npc" in ship.nickname:
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
                elif "ge_" in ship.nickname or "fl_" in ship.nickname:
                    built_by = "Civillian"
                elif "bw_" in ship.nickname:
                    built_by = "Borderworlds"
                elif "co_" in ship.nickname:
                    built_by = "Corsairs"
                elif "oc_" in ship.nickname:
                    built_by = "Outcasts"
                elif "col_" in ship.nickname:
                    built_by = "Crayter Republic"
                else:
                    built_by = ""

                sold_at = []
                for x in ship.sold_at():
                    sold_at.append(x.name())

                equipment = []
                for x in ship.equipment():
                    equipment.append(x.name())

                try:
                    hull_price = ship.hull().price
                except:
                    hull_price = 0
                
                try:
                    power_output = ship.power_core().capacity
                    power_recharge = ship.power_core().charge_rate
                except:
                    power_output = 0
                    power_recharge = 0

                ships[ship.name()] = {"nickname" : ship.nickname, "type" : ship.type(), "infocard" : ship.infocard(markup = 'html'), "infocard_plain" : ship.infocard(markup = 'plain') , "hull_price" : hull_price, "package_price" : ship.price(), "hit_pts" : ship.hit_pts, "hold_size" : ship.hold_size, "bot_limit" : ship.nanobot_limit, "bat_limit" : ship.shield_battery_limit, "power_output" : power_output, "power_recharge" : power_recharge, "built_by" : built_by, "equipment" : equipment, "sold_at" : sold_at}
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
            if commodity.classIsCommodity:
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
            if gun.classIsGun and gun.is_valid():
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
                if gun.classIsGun and gun.is_valid():
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

filename = "data.json"
print("Reading game files...")
startTime = time.time()
data = {"README" : f"This file was automatically generated by {path.basename(__file__)}. Do not edit unless you know what you're doing!",
        "Ships" : get_ships() ,"Systems" : get_systems(), "Bases" : get_bases(), "Commodities" : get_commodities(), "Guns" : get_guns()}
#midTime = time.time()
print(f"Game files read, writing {filename}...")
with open(f'D:\\repos\\flWiki\\{filename}', 'w') as f:
    json.dump(data, f, indent=1)
endTime = time.time()
print(f"Done.\nReading and writing took {round(endTime-startTime, 2)}s")