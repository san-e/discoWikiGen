import json
import math
from inspect import cleandoc
from itertools import zip_longest
from os import getcwd
from os.path import exists
import flint as fl
import re
from string import Template

from selenium.webdriver.support.expected_conditions import element_to_be_selected


def chunkList(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i: i + n]


def loadData(filename):
    with open(f"{getcwd()}/{filename}", "r") as file:
        data = json.load(file)
    return data

def filter_oorp_bases(
        bases, config
) -> list[fl.entities.Base] | dict | fl.entities.EntitySet[fl.entities.Base]:
    oorpBases = [b for b in fl.bases if b.system_().nickname in config["wikiGen"]["oorpSystems"]]
    if not bases:
        return {}
    if type(bases) == list:
        return list(filter(lambda x: x.nickname not in oorpBases, bases))
    elif type(bases) == dict:
        return dict(filter(lambda x: x[0].nickname not in oorpBases, bases.items()))
    elif type(bases) == fl.entities.EntitySet:
        return fl.entities.EntitySet(filter(lambda x: x.nickname not in oorpBases, bases.values()))
    raise ValueError("bases is of incompatible type " + type(bases))



def generateTable(header, entries, wikitable: bool = True, sortable: bool = False):
    _class = "wikitable " if wikitable else "" + "sortable " if sortable else ""
    table = f'{{| class="{_class}"\n! '
    formatting = set()
    for i, head in enumerate(header):
        if "price" in head.lower():
            formatting.add(i)
        table += f'{head} !!'
    table += "\n"

    for entry in entries:
        table += "|-\n| "
        for i, value in enumerate(entry):
            if i in formatting:
                table += f'{"{:,}".format(value)}$ || '
            else:
                table += f"[[{value}]] || "
        table += "\n"
    table += "|}\n"
    return table


def generateList(input_list):
    return "\n".join({f"* {x}\n" for x in input_list})


def generatePage(preset: str, config, nickname) -> str:
    houses = config["pageGen"]["houses"]
    corps = config["pageGen"]["corporations"]
    if preset.lower() == "ship":
        with open("./templates/ship.html", "r") as f:
            template = Template(f.read())

        ship: fl.entities.Ship = fl.get_ships()[nickname]

        name = ship.infocard("plain").split("\n")[0]
        image = f"{nickname}.png"
        ship_class = ship.type()
        #techcompat = ship_entry.techcompat
        gun_count = len([x for x in ship.hardpoints() if "weapon" in x.lower()])
        turret_count = len([x for x in ship.hardpoints() if "turret" in x.lower()])
        hull = "{:,}".format(ship.hit_pts)
        cargo = "{:,}".format(ship.hold_size)
        batteries = "{:,}".format(ship.shield_battery_limit)
        bots = "{:,}".format(ship.nanobot_limit)
        max_wep = max({int(re.findall("\\d+", nick)[-1]) for nick, hardpoint in ship.hardpoints().items() if any(x.category() == "weapons" for x in hardpoint)})
        max_shield = "{:,}".format(max({max({int(re.findall("\\d+", x.name())[-1]) for x in hardpoint}) for nick, hardpoint in ship.hardpoints().items() if "hpshield" in nick}))
        impulse = "{:,}".format(ship.impulse_speed())
        turnrate = "{:,}".format(math.degrees(ship.turn_rate()))
        power_output = "{:,}".format(ship.power_core().capacity)
        power_recharge = "{:,}".format(ship.power_core().charge_rate)
        max_cruise = "{:,}".format(ship.engine().cruise_speed if ship.engine().cruise_speed != 0 else fl.interface.get_constants()["engineequipconsts"]["cruising_speed"])
        hull_price = "{:,}".format(ship.hull().price)
        package_price = "{:,}".format(ship.price())
        torpedoCount = len([x for x in ship.hardpoints() if "torpedo" in x.lower()])
        mineCount = len([x for x in ship.hardpoints() if "mine" in x.lower()])
        cmCount = len([x for x in ship.hardpoints() if "cm" in x.lower()])
        thrusterCount = len(
            [x for x in ship.hardpoints() if "thruster" in x.lower()]
        )

        thruster_force = 72000
        engine = ship.engine()
        linear_drag = (
            ship.linear_drag + engine.linear_drag if engine else ship.linear_drag
        )
        force = thruster_force + ship.engine().max_force
        max_thrust = int(force / linear_drag) if thrusterCount > 0 else '<span style="color: #f7001d; font-style: italic;">Thruster not available</span>'
        other = ""
        if torpedoCount > 0:
            other += f'<li>{torpedoCount}xCD/T</li>\n'
        if cmCount > 0:
            other += f'<li>{cmCount}xCM</li>\n'
        if mineCount > 0:
            other += f'<li>{mineCount}xM</li>\n'

        info = ship.infocard().strip()

        hardpoints = ""
        hardpoint_names = [x[-1].name() for x in ship.hardpoints().values() if x[-1].name() != x[-1].nickname]
        for n in set(hardpoint_names):
            hardpoints = f"{hardpoints}<li>{hardpoint_names.count(n)}x {n}</li>\n"

        includes = ""
        for equip in ship.equipment():
            includes = f'{includes}<li>{equip.name()} (${"{:,}".format(equip.price())})</li>\n'

        return template.substitute(name = name,
                            image = image,
                            ship_class = ship_class,
                            techcompat = "",
                            gun_count = gun_count,
                            turret_count = turret_count,
                            max_wep = max_wep,
                            other = other,
                            hull = hull,
                            max_shield = max_shield,
                            cargo = cargo,
                            batteries = batteries,
                            bots = bots,
                            impulse = impulse,
                            turnrate = turnrate,
                            max_thrust = max_thrust,
                            max_cruise = max_cruise,
                            power_output = power_output,
                            power_recharge = power_recharge,
                            hull_price = hull_price,
                            package_price = package_price,
                            infocard = info,
                            moors = not ship.mission_property == "can_use_berths",
                            hardpoints = hardpoints,
                            includes = includes,
                            sold_at = generateTable(header=["Base", "Owner", "System", "Region"],
                                                                       entries={(x.name(), x.owner().name(),
                                                                                 x.system_().name(),
                                                                                 x.system_().region()) for x in
                                                                                ship.sold_at()}),
                            categories = f'[[Category: {ship.type()}]]'
                            )
    elif "sys" in preset.lower():
        with open("./templates/system.html", "r") as f:
            template = Template(f.read())

        entry = fl.get_systems()[nickname]

        suns = ""
        for star, card in entry.stars.items():
            suns += f"'''{star}'''\n"
            card = card[:-1]
            card = card.split("\n")
            for x in card:
                suns += f"* {x}\n"

        bases = set()
        lawfulFactions: set[fl.entities.universe.Faction] = set()
        unlawfulFactions: set[fl.entites.universe.Faction] = set()
        corporateFactions: set[fl.entities.universe.Faction] = set()

        for base in entry.bases():
            if not isinstance(base, fl.entities.solars.PlanetaryBase):
                bases.add(base)
            if base.owner() in corps:
                corporateFactions.add(base.owner())
            elif base.owner().legality() == "Lawful":
                lawfulFactions.add(base.owner())
            elif base.owner().legality() == "Unlawful":
                unlawfulFactions.add(base.owner())

        wrecks = ""
        for w in entry.wrecks():
            if (
                    "surprise" in w.nickname.lower()
                    or "suprise" in w.nickname.lower()
                    or "secret" in w.nickname.lower()
            ):
                wrecks += f"=== {w.name()} - {w.sector()} ===\n{w.infocard('html')}\n"
                if w.loot():
                    wrecks += """Contains:\n<ul style="margin-top:-15px;">\n"""
                    for item, amount in w.loot():
                        wrecks += f"<li>{amount}x [[{item.name()}]]</li>\n"
                    wrecks += "</ul>\n"



        return template.substitute(name = entry.name(),
                                   nickname = nickname,
                                   infocard = entry.infocard("html").split("Settled Planets")[0] + "</div>",
                                   government = f"{{{{House Link | {entry.region().title()} | long }}}}" if entry.region() in houses else entry.region().title(),
                                   region = entry.region().title(),
                                   neighbors = "\n".join([f"* {x.destination_system().name()}" for x in entry.connections() if x.destination_system().nickname not in config["wikiGen"]["oorpSystems"]]),
                                   lawful_factions = generateList(lawfulFactions),
                                   trade_factions = generateList(corporateFactions),
                                   unlawful_factions = generateList(unlawfulFactions),
                                   suns = suns,
                                   planets = generateTable(header=["Planet", "Owner"], entries=[(x.name(), x.owner().name()) for x in entry.planets()]),
                                   stations = generateTable(header=["Station", "Owner"], entries=[(x.name(), x.owner().name()) for x in bases]),
                                   fields = generateList([x.name() for x in entry.zones() if x.name() and (x.asteroids() or x.nebulae())]),
                                   mining_zones = entry.mineable_commodities(),

                                   navmap = f'[[File:{nickname}_map.png|center|750px|link={config["wikiGen"]["sysmapURL"]}#q={entry.name().replace(" ", "%20")}]]',
                                   nebulae = "\n".join([f"=== {x.name()} ===\n{x.infocard('html')}" for x in entry.zones() if x.nebulae()]),
                                   asteroids = "\n".join([f"=== {x.name()} ===\n{x.infocard('html')}" for x in entry.zones() if x.asteroids()]),
                                   wrecks = wrecks,
                                   gates = generateTable(header=["Target System", "Type", "Location"], entries=[(fl.get_systems()[x.goto[0]].name(), x.type(), x.sector()) for x in entry.connections()]))

    elif "base" in preset.lower():
        entry = fl.get_bases()[nickname]

        bribes_missions = generateTable(
            ["", "Offers Missions", "Offers Bribes"],
            [(f"'''{faction}'''", '✔' if faction in entry.missions() else '✗', '✔' if faction in entry.bribes() else '✗') for faction in entry.missions() + entry.bribes()]
        )

        econ_content = []
        for commodity in entry.buys_commodities() + entry.sells_commodities():
            sell = commodity.price
            if commodity in entry.sells_commodities():
                sell = [p for c, p in entry.sells().items() if c == commodity][0]
            buy = commodity.price
            if commodity in entry.buys_commodities():
                buy = [p for c, p in entry.buys().items() if c == commodity][0]
            average_sell = sum(commodity.sold_at().values()) / len(commodity.sold_at())
            average_buy = sum(commodity.bought_at().values()) / len(commodity.bought_at())
            sell_rating =   "-" if average_sell * 1.025 > sell > average_sell * 0.975 else \
                            "<span style:'color:green'>↗</span>" if sell > average_sell * 1.025 else \
                            "<span style:'color:red'>↘</span>"
            buy_rating =   "-" if average_buy * 1.025 > buy > average_buy * 0.975 else \
                            "<span style:'color:green'>↗</span>" if buy >= average_buy * 1.025 else \
                            "<span style:'color:red'>↘</span>"
            econ_content.append((commodity.name(), sell, buy, sell_rating, buy_rating))

        economy = generateTable(["Commodity", "Export Price", "Import Price", "Export Rating", "Import Rating"], econ_content)

        ships = generateTable(["Ship", "Class", "Price"], [(ship.name(), ship.type(), ship.price()) for ship in entry.ships_sold()])

        newsTemplate = '<table style="margin-bottom: 10px; margin-left: 1em; width:90%; border: 1px solid white;" cellpadding="3">\n<tr>\n<td style="text-align: center; font-size: larger; background: rgba(255, 255, 255, 0.2); color: #ffffff;"><b>{headline}</b>\n</td>\n</tr>\n<tr>\n<td style="padding-bottom: 7px; padding-left: 20px; padding-right: 20px">\n{news}\n</td>\n</tr>\n</table>\n'
        new = ""
        for headline, newsItem in entry.news:
            new = f'{new}{newsTemplate.replace("{headline}", headline).replace("{news}", newsItem)}\n'

        news = news.replace("{news}", new)

        rumorTemplate = '<table style="margin-bottom: 10px; margin-left: 1em; width:90%; border: 1px solid white;" cellpadding="3">\n<tr>\n<td style="text-align: center; font-size: larger; background: rgba(255, 255, 255, 0.2); color: #ffffff;"><b>[[{rumorFaction}]]</b>\n</td>\n</tr>\n<tr>\n<td style="padding-bottom: 7px;">\n{rumors}\n</td>\n</tr>\n</table>\n'
        rum = ""
        for faction, rumorList in entry.rumors.items():
            temp = "<ul>"
            for rumor in rumorList:
                temp = f"{temp}<li>{rumor.replace('&nbsp;', '')}</li><hr>\n"
            temp = f"{temp}</ul>"
            rum = f'{rum}{rumorTemplate.replace("{rumors}", temp).replace("{rumorFaction}", faction)}'

        rumors = rumors.replace("{rumors}", rum)

        other = f'[[Category: {entry.owner}]]\n[[Category: {entry.region}]]\n[[Category: {entry.system}]]\n'
        categories = categories.replace("{other}", other)

        return f"{infobox}{infocard}{bribesNmissions}{commodities}{ships}{news}{rumors}{categories}"
    elif "faction" in preset.lower():
        entry = data.factions[nickname]

        infobox = '__NOTOC__\n<table class="infobox bordered" style="float: right; margin-left: 1em; margin-bottom: 10px; width: 250px; font-size: 11px; line-height: 14px; border: 1px solid white;" cellpadding="3">\n\n<td colspan="2" style="text-align: center; font-size: 12px; line-height: 18px; background: rgba(255, 255, 255, 0.2); color: #ffffff", title = "{nickname}"><b>{name}</b>\n</td></tr>\n<tr>\n<td colspan="2" style="text-align: center; border: 1px solid white;"><div class="center"><div class="floatnone">[[File:{nickname}.png|center|250px]]</div></div>\n</td></tr>\n\n<tr>\n<td class="infobox-data-title"><b>Alignment</b>\n</td>\n<td style="padding-right: 1em">{alignment}\n</td></tr>\n</table>\n'
        infocard = "{infocard}\n"
        ships = '<h2 title="The ships this faction\'s NPC\'s use, as defined in faction_prop.ini">Ships used</h2>\n\n<table class="wikitable sortable">\n<tr>\n<th>Ship</th>\n<th>Class</th>\n</tr>\n{ships}\n</td></tr></table>\n'
        bases = '<h2 title="All bases that are owned by this faction">Bases owned</h2>\n\n<table class="wikitable collapsible mw-collapsible mw-collapsed">\n<tr>\n<th>\n</th>\n</tr>\n<tr>\n<td>\n<table class="wikitable sortable">\n<tr>\n<th>Base</th>\n<th>Owner</th>\n<th>System</th>\n<th>Region</th>\n</tr>\n{bases}\n</td></tr></table>\n</td></tr></table>\n'
        bribes_missions = '<h2 title="All bases that offer bribes for this faction">Bribes</h2>\n\n<table class="wikitable collapsible mw-collapsible mw-collapsed">\n<tr>\n<th>\n</th>\n</tr>\n<tr>\n<td>\n<table class="wikitable sortable">\n<tr>\n<th>Base</th>\n<th>Owner</th>\n<th>System</th>\n<th>Region</th>\n</tr>\n{bribes}\n</td></tr></table>\n</td></tr></table>\n'
        rep_sheet = '<h2 title="This faction\'s rep sheet">Diplomacy</h2>\n\n{{Reputation_Table/Start|caption=View Reputation|width=450px}}\n|-\n{repsheet}\n{{Reputation_Table/End}}\n'
        rumors = '<h2>Rumors</h2>\n<table class="wikitable collapsible mw-collapsible mw-collapsed">\n<tr>\n<th>\n</th>\n</tr>\n<tr>\n<td>\n{rumors}\n</td></tr></table>\n'
        time = "<i>NOTE: {time}<i>"
        categories = "\n[[Category: Factions]]\n"

        infobox = infobox.replace("{nickname}", nickname)
        infobox = infobox.replace("{name}", entry.name)
        infobox = infobox.replace("{alignment}", entry.alignment)

        infocard = infocard.replace("{infocard}", entry.infocard)

        shippos = ""
        for nick in entry.ships:
            ship = data.ships[nick]
            shippos = f"{shippos}<tr>\n<td>[[{ship.name}]]</td>\n<td>{ship.type}</td>\n</tr>\n"

        ships = ships.replace("{ships}", shippos)

        boses = ""
        for nick in entry.bases:
            base = data.bases[nick]
            boses = f"{boses}<tr>\n<td>[[{base.name}]]</td>\n<td>[[{base.owner}]]</td>\n<td>[[{base.system}]]</td>\n<td>{base.region}</td>\n</tr>\n"

        bases = bases.replace("{bases}", boses)

        brobes = ""
        for nick in entry.bribes:
            base = data.bases[nick]
            brobes = f"{brobes}<tr>\n<td>[[{base.name}]]</td>\n<td>[[{base.owner}]]</td>\n<td>[[{base.system}]]</td>\n<td>{base.region}</td>\n</tr>\n"

        bribes_missions = bribes_missions.replace("{bribes}", brobes)

        repsheet = ""
        split_reps = chunkList(list(entry.repsheet.keys()), len(entry.repsheet.keys()) // 2 + 1)
        for factions in zip_longest(*split_reps):
            for faction in factions:
                if not faction:
                    continue
                rep = entry.repsheet[faction]
                rep = f"+{rep}" if rep > 0 else rep
                repsheet = f"{repsheet}((RT|{faction}|{rep}))\n".replace("((", "{{").replace("))", "}}")
            repsheet = f"{repsheet}|-\n"

        rep_sheet = rep_sheet.replace("{repsheet}", repsheet[:-1])

        rum = ""
        rumorTemplate = '<table style="margin-bottom: 10px; margin-left: 1em; width:90%; border: 1px solid white;" cellpadding="3">\n<tr>\n<td style="text-align: center; font-size: larger; background: #555555; color: #ffffff;"><b>[[{rumorBase}]]</b>\n</td>\n</tr>\n<tr>\n<td style="padding-bottom: 7px;">\n{rumors}\n</td>\n</tr>\n</table>\n'
        for base, rumorList in entry.rumors.items():
            temp = "<ul>"
            for rumor in rumorList:
                temp = f"{temp}<li>{rumor.replace('&nbsp;', '')}</li><hr>\n"
            temp = f"{temp}</ul>"
            rum = f'{rum}{rumorTemplate.replace("{rumors}", temp).replace("{rumorBase}", base)}'

        rumors = rumors.replace("{rumors}", rum)

        return f"{infobox}{infocard}{ships}{bases}{bribes_missions}{rep_sheet}{rumors}{categories}"
    elif "commodity" in preset.lower():
        entry = data.commodities[nickname]

        infobox = '__NOTOC__\n<table class="infobox bordered" style=" margin-left: 1em; margin-bottom: 10px; font-size: 11px; line-height: 14px; border: 1px solid white; float: right" cellpadding="3">\n\n<td colspan="2" style="text-align: center; font-size: 12px; line-height: 18px; background: #555555; color: #ffffff" title="{nickname}"><b>{name}</b>\n</td></tr>\n<tr>\n<td colspan="2" style="text-align: center; border: 1px solid white;"><div class="center"><div class="floatnone">[[File:{nickname}.png|center|250px]]</div></div>\n</td></tr>\n\n<tr>\n<td class="infobox-data-title" title="The number of units of cargo this commodity uses"><b>Cargo Space</b>\n</td>\n<td style="padding-right: 1em">{volume}\n</td></tr>\n<tr>\n<td class="infobox-data-title" title="The rate at which this commodity decays per second"><b>Decay Rate</b>\n</td>\n<td style="padding-right: 1em">{decay}\n</td></tr>\n<tr>\n<td class="infobox-data-title"><b>Default Price</b>\n</td>\n<td style="padding-right: 1em">{price}\n</td></tr>\n<tr>\n<td class="infobox-data-title"><b>High Risk Commodity</b>\n</td>\n<td style="padding-right: 1em">{hrc}\n</td></tr>\n</table>\n'
        infocard = "{infocard}\n"
        availability = '<h2>Availability</h2>\n\n<table class="wikitable collapsible mw-collapsible mw-collapsed" style="margin-bottom: 10px; margin-left: 1em; border: 1px solid #47505a;" cellpadding="3">\n<tr>\n<td style="text-align: center; font-size: larger; background: #555555; color: #ffffff;" title="All bases which buy this commodity"><b>Bases buying</b>\n</td>\n</tr>\n<tr>\n<td style="padding-bottom: 7px;">\n<table class="wikitable sortable">\n<tr>\n<th>Base</th>\n<th>Owner</th>\n<th>System</th>\n<th>Region</th>\n<th>Price</th>\n</tr>\n{buyBases}\n</td></tr></table>\n\n</td>\n</tr>\n</table>\n<table class="wikitable collapsible mw-collapsible mw-collapsed" style="margin-bottom: 10px; margin-left: 1em; border: 1px solid white;" cellpadding="3">\n<tr>\n<td style="text-align: center; font-size: larger; background: #555555; color: #ffffff;" title="All bases which sell this commodity"><b>Bases selling</b>\n</td>\n</tr>\n<tr>\n<td style="padding-bottom: 7px;">\n<table class="wikitable sortable">\n<tr>\n<th>Base</th>\n<th>Owner</th>\n<th>System</th>\n<th>Region</th>\n<th>Price</th>\n</tr>\n{sellBases}\n</td></tr></table>\n</td>\n</tr>\n</table>\n<p><br style="clear: both; height: 0px;" />\n<br style="clear: both; height: 0px;" />\n'
        categories = "[[Category: Commodities]]\n"

        infobox = infobox.replace("{nickname}", nickname)
        infobox = infobox.replace("{name}", entry.name)
        infobox = infobox.replace("{volume}", str(entry.volume))
        infobox = infobox.replace("{decay}", str(entry.decay) if entry.decay else "<i>no decay</i>")
        infobox = infobox.replace("{price}", "{:,}".format(entry.defaultPrice) + "$")
        infobox = infobox.replace("{hrc}", str(entry.hrc))

        infocard = infocard.replace("{infocard}", entry["infocard"].replace("&nbsp;", ""))

        boughtAt = ""
        soldAt = ""
        for nick in entry.boughtAt:
            base = data.bases[nick]
            boughtAt = f"{boughtAt}<tr>\n<td>[[{base.name}]]</td>\n<td>[[{base.owner}]]</td>\n<td>[[{base.system}]]</td>\n<td>{base.region}</td>\n<td>{'{:,}'.format(base.equipment_selling[nickname])}$</td>\n</tr>\n"
        for nick in entry.soldAt:
            base = data.bases[nick]
            soldAt = f"{soldAt}<tr>\n<td>[[{base.name}]]</td>\n<td>[[{base.owner}]]</td>\n<td>[[{base.system}]]</td>\n<td>{base.region}</td>\n<td>{'{:,}'.format(base.equipment_selling[nickname])}$</td>\n</tr>\n"

        availability = availability.replace("{buyBases}", boughtAt)
        availability = availability.replace("{sellBases}", soldAt)

        return f"{infobox}{infocard}{availability}{categories}"
    elif "weapon" in preset.lower():
        entry = data.weapons[nickname]

        infobox = """__NOTOC__\n<table class="infobox bordered" style="float: right; margin-left: 1em; margin-bottom: 10px; font-size: 11px; line-height: 14px; border: 1px solid white;" cellpadding="3">\n\n<td colspan="2" style="text-align: center; font-size: 12px; line-height: 18px; background: rgba(255, 255, 255, 0.2); color: #ffffff" title="{nickname}"><b>{name}</b>\n</td></tr>\n<tr>\n<td colspan="2" style="text-align: center; border: 1px solid white;"><div class="center"><div class="floatnone">[[File:{icon_name}|center|128px]]</div></div>\n</td></tr>\n\n<tr>\n<td class="infobox-data-title" title="Hull Damage per hit"><b>Hull Damage</b>\n</td>\n<td style="padding-right: 1em">{hull_damage}\n</td>\n</tr>\n<tr>\n<td class="infobox-data-title" title="Shield Damage per hit"><b>Shield Damage</b>\n</td>\n<td style="padding-right: 1em">{shield_damage}\n</td>\n</tr>\n<tr>\n<td class="infobox-data-title" title="Hull Damage per second of continuous fire"><b>Hull Damage/s</b>\n</td>\n<td style="padding-right: 1em">{hull_dps}\n</td>\n</tr>\n<tr>\n<td class="infobox-data-title" title="Shield Damage per second of continuous fire"><b>Shield Damage/s</b>\n</td>\n<td style="padding-right: 1em">{shield_dps}\n</td>\n</tr>\n<tr>\n<td class="infobox-data-title" title="Amound of projectiles shot per second"><b>Refire Rate</b>\n</td>\n<td style="padding-right: 1em">{refire}\n</td>\n</tr>\n<tr>\n<td class="infobox-data-title" title="Amount of energy used per second"><b>Energy usage/s</b>\n</td>\n<td style="padding-right: 1em">{energy_usage}\n</td>\n</tr>\n<tr>\n<td class="infobox-data-title" title="Speed of the projectile in meters per second"><b>Projectile Velocity</b>\n</td>\n<td style="padding-right: 1em">{speed}\n</td>\n</tr>\n<tr>\n<td class="infobox-data-title" title="Range of the projectile in meters"><b>Range</b>\n</td>\n<td style="padding-right: 1em">{range}\n</td>\n</tr>\n<tr>\n<td class="infobox-data-title" title="(Hull Damage + Shield Damage) / Power Usage"><b>Efficiency</b>\n</td>\n<td style="padding-right: 1em">{efficiency}\n</td>\n</tr>\n<tr>\n<td class="infobox-data-title" title="FLStat Rating"><b>FLStat Rating</b>\n</td>\n<td style="padding-right: 1em">{rating}\n</td>\n</tr>\n</table>\n\n"""
        infocard = "{infocard}\n"
        availability = "<h2>Availability</h2>\n{availability}"
        time = "<i>NOTE: {time}</i>\n"
        categories = "\n[[Category: Weapons]]{type}\n"

        infobox = infobox.replace("{nickname}", nickname)
        infobox = infobox.replace("{name}", entry.shortName)
        infobox = infobox.replace("{icon_name}", f'{entry.icon_name}.png')
        infobox = infobox.replace("{hull_damage}", str(entry.hull_damage))
        infobox = infobox.replace("{shield_damage}", str(entry.shield_damage))
        infobox = infobox.replace("{hull_dps}", str(entry.hull_dps))
        infobox = infobox.replace("{shield_dps}", str(entry.shield_dps))
        infobox = infobox.replace("{refire}", str(entry.refire))
        infobox = infobox.replace("{energy_usage}", str(entry.energy_per_second))
        infobox = infobox.replace("{speed}", str(entry.speed))
        infobox = infobox.replace("{range}", str(entry.range))
        infobox = infobox.replace("{efficiency}", str(entry.efficiency))
        infobox = infobox.replace("{rating}", str(entry.rating))

        infocard = infocard.replace("{infocard}",
                                    entry.infocard.replace("<p>", '<p style="padding: 0px; margin: 0px;">').replace(
                                        '<p align="left">',
                                        '<p style="padding: 0px; margin: 0px;">'), )

        temp = ""
        if entry.sold_at:
            temp = (
                    temp + f"""<h3>Sold at</h3>\n{generateTable(["Name", "Owner", "System", "Region", "Price"], ((data.bases[x].name, data.bases[x].owner, data.bases[x].system, data.bases[x].region, data.bases[x].) for x in entry.sold_at))}\n""")

        if entry["wrecks"]:
            temp = (temp + f"""<h3>Wrecks</h3>\n{generateTable(["Name", "System", "Sector"], entry["wrecks"])}""")

        availability = availability.replace("{availability}", temp)

        time = time.replace("{time}", entry["time"])

        if entry["shortName"].isupper():
            categories = categories.replace("{type}",
                                            f"[[Category: {entry['type'].title()}]] [[Category: Codenames]]", )
        else:
            categories = categories.replace("{type}", f"[[Category: {entry['type'].title()}]]")

        return f"{infobox}{infocard}{availability}{categories}"
    elif "cm" in preset.lower():
        entry = data["Equipment"]["CounterMeasures"][nickname]

        infobox = """__NOTOC__\n<table class="infobox bordered" style="float: right; margin-left: 1em; margin-bottom: 10px; font-size: 11px; line-height: 14px; border: 1px solid white;" cellpadding="3">\n\n<td colspan="2" style="text-align: center; font-size: 12px; line-height: 18px; background: rgba(255, 255, 255, 0.2); color: #ffffff" title="{nickname}"><b>{name}</b>\n</td></tr>\n<tr>\n<td colspan="2" style="text-align: center; border: 1px solid white;"><div class="center"><div class="floatnone">[[File:{icon_name}.png|center|250px]]</div></div>\n</td></tr>\n\n<tr>\n<td class="infobox-data-title" title="The price of this CM-Dropper"><b>Price</b>\n</td>\n<td style="padding-right: 1em">{price}\n</td></tr>\n<tr>\n<td class="infobox-data-title" title="The price of this CM-Dropper's flares"><b>Flare Price</b>\n</td>\n<td style="padding-right: 1em">{flare_price}\n</td></tr>\n<tr>\n<td class="infobox-data-title" title="The maximum amount of carriable Flares"><b>Max. Flares</b>\n</td>\n<td style="padding-right: 1em">{flare_count}\n</td></tr>\n<td class="infobox-data-title" title="The probability this countermeasure will defeat an incoming missile."><b>Effectiveness</b>\n</td>\n<td style="padding-right: 1em">{effectiveness}\n</td></tr>\n<td class="infobox-data-title" title="The Range the Flare will travel, in meters"><b>Range</b>\n</td>\n<td style="padding-right: 1em">{range}\n</td></tr>\n<td class="infobox-data-title" title="The time this Flare will stay alive for"><b>Lifetime</b>\n</td>\n<td style="padding-right: 1em">{lifetime}\n</td></tr>\n</table>\n"""
        infocard = "{infocard}\n"
        availability = "<h3>Availability</h3>\n{sold_at}\n"
        categories = "[[Category: Equipment]]\n[[Category: Countermeasures]]\n"

        infobox = infobox.replace("{nickname}", nickname)
        infobox = infobox.replace("{name}", entry["name"])
        infobox = infobox.replace("{icon_name}", entry["icon_name"])
        infobox = infobox.replace("{price}", "{:,}".format(entry["price"]) + "$")
        infobox = infobox.replace("{flare_price}", "{:,}".format(entry["flare_price"]) + "$")
        infobox = infobox.replace("{flare_count}", str(entry["max_flares"]))
        infobox = infobox.replace("{effectiveness}", str(entry["effectiveness"] * 100) + "%")
        infobox = infobox.replace("{range}", str(entry["range"]) + "m")
        infobox = infobox.replace("{lifetime}", str(entry["lifetime"]) + "s")

        infocard = infocard.replace("{infocard}", entry["infocard"])

        if entry["availability"]:
            availability = availability.replace("{sold_at}",
                                                generateTable(header=["Base", "Owner", "System", "Region", "Price"],
                                                              entries=entry["availability"], ), )
        else:
            availability = availability.replace("{sold_at}", "")

        return f"{infobox}{infocard}{availability}{categories}"
    elif "armor" in preset.lower():
        entry = data["Equipment"]["Armor"][nickname]

        infobox = """__NOTOC__\n<table class="infobox bordered" style="float: right; margin-left: 1em; margin-bottom: 10px; font-size: 11px; line-height: 14px; border: 1px solid white;" cellpadding="3">\n\n<td colspan="2" style="text-align: center; font-size: 12px; line-height: 18px; background: rgba(255, 255, 255, 0.2); color: #ffffff" title="{nickname}"><b>{name}</b>\n</td></tr>\n<tr>\n<td colspan="2" style="text-align: center; border: 1px solid white;"><div class="center"><div class="floatnone">[[File:{icon_name}.png|center|250px]]</div></div>\n</td></tr>\n\n<tr>\n<td class="infobox-data-title" title="The price of this Armor Upgrade"><b>Price</b>\n</td>\n<td style="padding-right: 1em">{price}\n</td></tr>\n<tr>\n<td class="infobox-data-title" title="The amount of cargo this Armor Upgrade uses"><b>Volume</b>\n</td>\n<td style="padding-right: 1em">{volume}\n</td></tr>\n<tr>\n<td class="infobox-data-title" title="The amount by which the ship's health is multiplied"><b>Multiplier</b>\n</td>\n<td style="padding-right: 1em">{multiplier}\n</td></tr>\n</table>\n"""
        infocard = "{infocard}\n"
        availability = "<h3>Availability</h3>\n{sold_at}\n"
        categories = "[[Category: Equipment]]\n[[Category: Armor]]\n"

        infobox = infobox.replace("{nickname}", nickname)
        infobox = infobox.replace("{name}", entry["name"])
        infobox = infobox.replace("{icon_name}", entry["icon_name"])
        infobox = infobox.replace("{price}", "{:,}".format(entry["price"]) + "$")
        infobox = infobox.replace("{volume}", str(entry["volume"]))
        infobox = infobox.replace("{multiplier}", str(entry["multiplier"]) + "x")

        infocard = infocard.replace("{infocard}", entry["infocard"])

        if entry["availability"]:
            availability = availability.replace("{sold_at}",
                                                generateTable(header=["Base", "Owner", "System", "Region", "Price"],
                                                              entries=entry["availability"], ), )
        else:
            availability = availability.replace("{sold_at}", "")

        return f"{infobox}{infocard}{availability}{categories}"
    elif "cloak" in preset.lower():
        entry = data["Equipment"]["Cloaks"][nickname]
        infobox = """__NOTOC__\n<table class="infobox bordered" style="float: right; margin-left: 1em; margin-bottom: 10px; font-size: 11px; line-height: 14px; border: 1px solid white;" cellpadding="3">\n\n<td colspan="2" style="text-align: center; font-size: 12px; line-height: 18px; background: rgba(255, 255, 255, 0.2); color: #ffffff" title="{nickname}"><b>{name}</b>\n</td></tr>\n<tr>\n<td colspan="2" style="text-align: center; border: 1px solid white;"><div class="center"><div class="floatnone">[[File:{icon_name}.png|center|250px]]</div></div>\n</td></tr>\n\n<tr>\n<td class="infobox-data-title" title="The price of this Cloak (Likely not what you'll actually be paying to other players)"><b>Price</b>\n</td>\n<td style="padding-right: 1em">{price}\n</td></tr>\n</table>\n"""
        infocard = "{infocard}\n"
        availability = "<h3>Availability</h3>\n{sold_at}\n"
        categories = "[[Category: Equipment]]\n[[Category: Cloaks]]\n"

        infobox = infobox.replace("{nickname}", nickname)
        infobox = infobox.replace("{name}", entry["name"])
        infobox = infobox.replace("{icon_name}", entry["icon_name"])
        infobox = infobox.replace("{price}", "{:,}".format(entry["price"]) + "$")
        infobox = infobox.replace("{volume}", str(entry["volume"]))

        infocard = infocard.replace("{infocard}", entry["infocard"])

        if entry["availability"]:
            availability = availability.replace("{sold_at}",
                                                generateTable(header=["Base", "Owner", "System", "Region", "Price"],
                                                              entries=entry["availability"], ), )
        else:
            availability = availability.replace("{sold_at}", "")

        return f"{infobox}{infocard}{availability}{categories}"
    elif "engine" in preset.lower():
        entry = data["Equipment"]["Engines"][nickname]
        infobox = """__NOTOC__\n<table class="infobox bordered" style="float: right; margin-left: 1em; margin-bottom: 10px; font-size: 11px; line-height: 14px; border: 1px solid white;" cellpadding="3">\n\n<td colspan="2" style="text-align: center; font-size: 12px; line-height: 18px; background: rgba(255, 255, 255, 0.2); color: #ffffff" title="{nickname}"><b>{name}</b>\n</td></tr>\n<tr>\n<td colspan="2" style="text-align: center; border: 1px solid white;"><div class="center"><div class="floatnone">[[File:{icon_name}.png|center|250px]]</div></div>\n</td></tr>\n\n<tr>\n<td class="infobox-data-title" title="The price of this Engine"><b>Price</b>\n</td>\n<td style="padding-right: 1em">{price}\n</td></tr>\n<td class="infobox-data-title" title="The maximum cruise speed this engine can reach"><b>Max. Cruise Speed</b>\n</td>\n<td style="padding-right: 1em">{cruise_speed}\n</td></tr>\n<td class="infobox-data-title" title="The time it takes to reach Cruise"><b>Cruise Charge Time</b>\n</td>\n<td style="padding-right: 1em">{cruise_charge_time}\n</td></tr>\n</table>\n"""
        infocard = "{infocard}\n"
        availability = "<h3>Availability</h3>\n{sold_at}\n"
        categories = "[[Category: Equipment]]\n[[Category: Engines]]\n"

        infobox = infobox.replace("{nickname}", nickname)
        infobox = infobox.replace("{name}", entry["name"])
        infobox = infobox.replace("{icon_name}", entry["icon_name"])
        infobox = infobox.replace("{price}", "{:,}".format(entry["price"]) + "$")
        infobox = infobox.replace("{cruise_speed}", str(entry["cruise_speed"]))
        infobox = infobox.replace("{cruise_charge_time}", str(entry["cruise_charge_time"]))

        infocard = infocard.replace("{infocard}", entry["infocard"])

        if entry["availability"]:
            availability = availability.replace("{sold_at}",
                                                generateTable(header=["Base", "Owner", "System", "Region", "Price"],
                                                              entries=entry["availability"], ), )
        else:
            availability = availability.replace("{sold_at}", "")

        return f"{infobox}{infocard}{availability}{categories}"
    elif "shield" in preset.lower():
        entry = data["Equipment"]["Shields"][nickname]
        infobox = """__NOTOC__\n<table class="infobox bordered" style="float: right; margin-left: 1em; margin-bottom: 10px; font-size: 11px; line-height: 14px; border: 1px solid white;" cellpadding="3">\n\n<td colspan="2" style="text-align: center; font-size: 12px; line-height: 18px; background: rgba(255, 255, 255, 0.2); color: #ffffff" title="{nickname}"><b>{name}</b>\n</td></tr>\n<tr>\n<td colspan="2" style="text-align: center; border: 1px solid white;"><div class="center"><div class="floatnone">[[File:{icon_name}.png|center|250px]]</div></div>\n</td></tr>\n\n<tr>\n<td class="infobox-data-title" title="The price of this shield"><b>Price</b>\n</td>\n<td style="padding-right: 1em">{price}\n</td></tr>\n<td class="infobox-data-title" title="This shields capacity"><b>Capacity</b>\n</td>\n<td style="padding-right: 1em">{capacity}\n</td></tr>\n<td class="infobox-data-title" title="Amount of capacity regenerated per second"><b>Regeneration Rate</b>\n</td>\n<td style="padding-right: 1em">{regen_rate}\n</td></tr>\n<td class="infobox-data-title" title="The time it takes to rebuild in seconds"><b>Offline Rebuild Time</b>\n</td>\n<td style="padding-right: 1em">{rebuild_time}\n</td></tr>\n<td class="infobox-data-title" title="Amount of energy consumed on rebuild"><b>Rebuild Power Draw</b>\n</td>\n<td style="padding-right: 1em">{rebuild_power_draw}\n</td></tr>\n<td class="infobox-data-title" title="Amount of energy consumed every second"><b>Constant Power Draw</b>\n</td>\n<td style="padding-right: 1em">{constant_power_draw}\n</td></tr>\n<td class="infobox-data-title"><b>Offline Threshold</b>\n</td>\n<td style="padding-right: 1em">{offline_threshold}\n</td></tr>\n<td class="infobox-data-title"><b>Technology</b>\n</td>\n<td style="padding-right: 1em">{technology}\n</td></tr>\n</table>\n"""
        infocard = "{infocard}\n"
        availability = "<h3>Availability</h3>\n{sold_at}\n"
        categories = "[[Category: Equipment]]\n[[Category: Shields]]\n{technology}\n"

        infobox = infobox.replace("{name}", entry["name"])
        infobox = infobox.replace("{nickname}", nickname)
        infobox = infobox.replace("{icon_name}", entry["icon_name"])
        infobox = infobox.replace("{price}", "{:,}".format(entry["price"]) + "$")
        infobox = infobox.replace("{capacity}", "{:,}".format(round(entry["capacity"], 2)))
        infobox = infobox.replace("{regen_rate}", str(round(entry["regen_rate"], 2)))
        infobox = infobox.replace("{rebuild_time}", str(entry["offline_rebuild_time"]))
        infobox = infobox.replace("{rebuild_power_draw}", str(entry["rebuild_power_draw"]))
        infobox = infobox.replace("{constant_power_draw}", str(entry["constant_power_draw"]))
        infobox = infobox.replace("{offline_threshold}", str(entry["offline_threshold"]))
        infobox = infobox.replace("{technology}", f'{entry["technology"]}')

        infocard = infocard.replace("{infocard}", entry["infocard"])

        if entry["availability"]:
            availability = availability.replace("{sold_at}",
                                                generateTable(header=["Base", "Owner", "System", "Region", "Price"],
                                                              entries=entry["availability"], ), )
        else:
            availability = availability.replace("{sold_at}", "")

        categories = categories.replace("{technology}", f'[[Category: {entry["technology"]}]]')

        return f"{infobox}{infocard}{availability}{categories}"
    raise ValueError("template is not a valid template")


def generateSpecial(ships={}, systems={}, bases={}, factions={}, commodities={}):
    shipTemplate0 = """A list of all ships in this wiki. Click [Expand] below to show a sortable table of all ships\n\n{| class="sortable wikitable mw-collapsible mw-collapsed" width="100%"\n|+ \n|-\n!rowspan="2" style="text-align: center;"|Name\n!rowspan="2" style="text-align: center;"|Techcell\n!rowspan="2" style="text-align: center;"|Class\n!rowspan="1" style="text-align: center;"|Guns\n!rowspan="1" style="text-align: center;"|Turrets\n!rowspan="1" style="text-align: center;"|Mines\n!rowspan="1" style="text-align: center;"|CDs/Ts\n!rowspan="1" style="text-align: center;"|CMs\n!rowspan="2" style="text-align: center;"|Turn<br>Rate\n!rowspan="2" style="text-align: center;"|Hit<br>Points\n!rowspan="2" style="text-align: center;"|Power<br>Core\n!rowspan="2" style="text-align: center;"|Nanobots\n!rowspan="2" style="text-align: center;"|Shield Batteries\n!rowspan="2" style="text-align: center;"|Hold<br>Size\n!rowspan="2" style="text-align: center;"|Package<br>Price\n|-\n!colspan="6" style="text-align: center;"|Hardpoint Types\n"""
    shipTemplate1 = """|-\n|{name}\n|{faction}\n|{class}\n|style="text-align: center;"|{guns}\n|style="text-align: center;"|{turrets}\n|style="text-align: center;"|{mines} \n|style="text-align: center;"|{cds}\n|style="text-align: center;"|{cms}\n|style="text-align: center;"|{turnrate}\n|style="text-align: center;"|{hitpoints}\n|style="text-align: center;"|{powercore}\n|style="text-align: center;"|{bots}\n|style="text-align: center;"|{bats}\n|style="text-align: center;"|{cargo} \n|style="text-align: center;"|{price}"""

    pages = {}

    temps = ""
    for nickname, attributes in ships.items():
        temps = f"{temps}\n{shipTemplate1}"

        temps = temps.replace("{name}", f'[[{attributes["name"]}]]')
        temps = temps.replace("{faction}", str(attributes["techcompat"]))
        temps = temps.replace("{class}", str(attributes["type"]))
        temps = temps.replace("{guns}", str(attributes["gunCount"]))
        temps = temps.replace("{turrets}", str(attributes["turretCount"]))
        temps = temps.replace("{mines}", str(attributes["mineCount"]))
        temps = temps.replace("{cds}", str(attributes["torpedoCount"]))
        temps = temps.replace("{cms}", str(attributes["cmCount"]))
        temps = temps.replace("{turnrate}", str(attributes["turnRate"]))
        temps = temps.replace("{hitpoints}", "{:,}".format(attributes["hit_pts"]))
        temps = temps.replace("{powercore}", "{:,}".format(attributes["power_output"]))
        temps = temps.replace("{bots}", str(attributes["bot_limit"]))
        temps = temps.replace("{bats}", str(attributes["bat_limit"]))
        temps = temps.replace("{cargo}", str(attributes["hold_size"]))
        temps = temps.replace("{price}", "$" + "{:,}".format(attributes["package_price"]))
    pages["Category:Ships"] = f"{shipTemplate0}{temps}\n" + "|}\n<hr>"

    commodityTemplate0 = """A list of all commodities in this wiki. Click [Expand] below to show a sortable table of all commodities\n\n{| class="sortable wikitable mw-collapsible mw-collapsed" width="100%"\n|+ \n|-\n! Commodity\n! Cargo Space\n! Decay rate<br />\n! Default price\n{a}\n|}\n<hr>"""
    commodityTemplate1 = """|-\n| {name}\n| {cargo}\n| {decay}\n| {price}\n"""

    temps = ""
    for nickname, attributes in commodities.items():
        temps = f"{temps}\n{commodityTemplate1}"
        temps = temps.replace("{name}", f'[[{attributes["name"]}]]')
        temps = temps.replace("{cargo}", "{:,}".format(int(attributes["volume"])))
        temps = temps.replace("{decay}", "{:,}".format(attributes["decay"]))
        temps = temps.replace("{price}", "$" + "{:,}".format(attributes["defaultPrice"]))
    pages["Category:Commodities"] = commodityTemplate0.replace("{a}", temps)

    return pages


def assemblePages():
    configData = loadData("config.json")
    sources = {}
    redirects = {}

    print("Assembling pages\n===================")

    sysSource = {}
    print("Assembling System pages")
    for name, system in data.systems.items():
        source = (generatePage(preset="System", config=configData,
                               nickname=name) + "[[Category: NukeOnPatch]]")
        sysSource[system.name] = source
    sources["Systems"] = sysSource

    shipSource = {}
    print("Assembling Ship pages")
    for name, ship in data.ships.items():
        source = (generatePage(preset="Ship", config=configData,
                               nickname=name) + "[[Category: NukeOnPatch]]")
        shipSource[ship.name] = source
        if ship.name != ship.longName:
            redirects[ship.longName] = (f"""#REDIRECT[[{ship.name}]] [[Category: NukeOnPatch]]""")
    sources["Ships"] = shipSource

    baseSource = {}
    print("Assembling Base pages")
    for name, base in data.bases.items():
        source = (generatePage(preset="Base", config=configData,
                               nickname=name) + "[[Category: NukeOnPatch]]")
        name = (base.name if base.name not in sources["Ships"].keys() else f'{base.name} (b)')
        baseSource[name] = source
    sources["Bases"] = baseSource

    factionSource = {}
    print("Assembling Faction pages")
    for name, faction in data.factions.items():
        if not "Guard" in faction.name:
            source = (generatePage(preset="Faction", config=configData,
                                   nickname=name, ) + "[[Category: NukeOnPatch]]")
            factionSource[faction.name] = source
            if faction.name != faction.shortName:
                redirects[faction.shortName] = (f"""#REDIRECT[[{faction.name}]] [[Category: NukeOnPatch]]""")
    sources["Factions"] = factionSource

    commoditySource = {}
    print("Assembling Commodity pages")
    for name, commodity in data.commodities.items():
        source = (generatePage(preset="Commodity", config=configData,
                               nickname=name) + "[[Category: NukeOnPatch]]")
        commoditySource[commodity.name] = source
    sources["Commodities"] = commoditySource

    weaponSource = {}
    print("Assembling Weapon pages")
    for name, weapon in data.weapons.items():
        source = (generatePage(preset="Weapon", config=configData,
                               nickname=name) + "[[Category: NukeOnPatch]]")
        weaponSource[weapon.name] = source
    sources["Weapons"] = weaponSource

    equipment = data.equipment
    cmSource = {}
    print("Assembling CM pages")
    for name, cm in (x for x in equipment.items() if isinstance(x, CountermeasureEntry)):
        source = (
                generatePage(preset="CM", config=configData, nickname=name) + "[[Category: NukeOnPatch]]")
        cmSource[cm["name"]] = source
    sources["CMs"] = cmSource

    armorSource = {}
    print("Assembling Armor pages")
    for name, armor in (x for x in equipment.items() if isinstance(x, ArmorEntry)):
        source = (generatePage(preset="Armor", config=configData,
                               nickname=name) + "[[Category: NukeOnPatch]]")
        armorSource[armor["name"]] = source
    sources["Armor"] = armorSource

    cloakSource = {}
    print("Assembling Cloak pages")
    for name, cloak in (x for x in equipment.items() if isinstance(x, ArmorEntry)):
        source = (generatePage(preset="Cloak", config=configData,
                               nickname=name) + "[[Category: NukeOnPatch]]")
        cloakSource[cloak["name"]] = source
    sources["Cloaks"] = cloakSource

    engineSource = {}
    print("Assembling Engine pages")
    for name, engine in (x for x in equipment.items() if isinstance(x, EngineEntry)):
        source = (generatePage(preset="Engine", config=configData,
                               nickname=name) + "[[Category: NukeOnPatch]]")
        engineSource[engine["name"]] = source
    sources["Engines"] = engineSource

    shieldSource = {}
    print("Assembling Shield pages")
    for name, shield in (x for x in equipment.items() if isinstance(x, ShieldEntry)):
        source = (generatePage(preset="Shield", config=configData,
                               nickname=name) + "[[Category: NukeOnPatch]]")
        shieldSource[shield.name] = source
    sources["Shields"] = shieldSource

    print("Assembling Redirect pages")
    sources["Redirects"] = redirects

    print("Assembling Special pages")
    sources["Special"] = generateSpecial(ships=data.ships, bases=data.bases, systems=data.systems,
                                         factions=data.factions, commodities=data.commodities)

    return sources


def main():
    sources = assemblePages()
    print("DONE")
    return sources
