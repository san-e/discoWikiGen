import json
import math
import os
import re
from collections import defaultdict
from collections.abc import Iterable
from functools import lru_cache
from os import getcwd
from pathlib import PureWindowsPath
from string import Template

import flint as fl
from flint.entities import (
    EntitySet,
    Commodity,
    Gun,
    Faction,
    Ship,
    Base,
    System,
    ShipPackage,
    Good,
    Entity,
    Solar,
    Planet,
    BaseSolar,
)
from flint.formats import ini, dll

# Set working directory to scripts folder
os.chdir(os.path.dirname(os.path.abspath(__file__)))

BAR = "{{!}}"
DBAR = "{{!!}}"


def chunk_list(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def icon_name(path):
    return os.path.splitext(PureWindowsPath(path).parts[-1])[0]


def load_data(filename):
    with open(f"{getcwd()}/{filename}", "r") as file:
        data = json.load(file)
    return data


def load_template(template: str) -> Template:
    with open(f"./templates/{template}.html", "r") as f:
        template = Template(f.read())
    return template


CONFIG = load_data("config.json")


def filter_oorp_bases(
    bases,
) -> set[Base] | dict | EntitySet[Base]:
    if not bases:
        return {}
    if isinstance(bases, dict):
        return dict(
            x
            for x in bases.items()
            if x[0].system_().nickname not in CONFIG["wikiGen"]["oorpSystems"]
        )
    elif isinstance(bases, EntitySet):
        return EntitySet(
            x
            for x in bases
            if x.system_().nickname not in CONFIG["wikiGen"]["oorpSystems"]
        )
    elif isinstance(bases, Iterable):
        return set(
            x
            for x in bases
            if x.system_().nickname not in CONFIG["wikiGen"]["oorpSystems"]
        )
    raise ValueError("bases is of incompatible type " + str(type(bases)))


def filter_bases(bases: Iterable[Base]) -> EntitySet[Base]:
    return EntitySet(base for base in filter_oorp_bases(bases) if base.has_solar())


def filter_ships(ships: Iterable[Ship]) -> EntitySet[Ship]:
    ships_in_pob_recipes = get_pob_recipes_ships()
    return EntitySet(
        ship
        for ship in ships
        if (
            ship.good()  # a ship without a good can't be purchased or crafted, therefore we shouldn't consider it
            and (  # check for obtainability basically
                ship in ships_in_pob_recipes  # can be crafted
                or filter_oorp_bases(ship.sold_at())  # is sold somewhere
            )
        )
    )


def filter_systems(systems: Iterable[System]) -> EntitySet[System]:
    return EntitySet(
        system
        for system in systems
        if system.nickname not in CONFIG["wikiGen"]["oorpSystems"]
    )


def filter_factions(factions: Iterable[Faction]) -> EntitySet[Faction]:
    return EntitySet(
        x for x in factions if not x.nickname.lower() in x.name().lower() and x.name()
    )


def filter_commodities(commodities: Iterable[Commodity]) -> EntitySet[Commodity]:
    return EntitySet(
        c
        for c in commodities
        if filter_bases(c.sold_at())
        or filter_bases(c.bought_at())
        or filter_systems(c.mineable_in())
    )


def generate_table(
    header,
    entries,
    wikitable: bool = True,
    sortable: bool = False,
    title: str = "",
    style: str = "",
):
    _class = ("wikitable " if wikitable else "") + ("sortable " if sortable else "")
    table = f'{{{BAR} class="{_class}" style="{style}"\n'
    if title:
        table += f"{BAR}+ {title}\n"
    table += "! "
    formatting = set()
    for i, head in enumerate(header):
        if "price" in head.lower():
            formatting.add(i)
        table += f"{head} !!"
    table = table[:-2]  # chop off the last !!
    table += "\n"

    for entry in entries:
        table += f"{BAR}-\n{BAR} "
        for i, value in enumerate(entry):
            if i in formatting:
                table += f'{"{:,}".format(value)}$ {DBAR} '
            else:
                table += f"{value} {DBAR} "
        table = table[: -(len(DBAR) + 1)]  # chop off the last DBAR
        table += "\n"
    table += f"{BAR}}}\n"
    return table


def rumor_tabber(entry: Faction | Base) -> str:
    tabber = "<tabber>\n"
    for base, rumors in sorted(
        entry.rumors().items(), key=lambda x: len(x[1]), reverse=True
    ):
        tabber += f"|-|{base.name()} ({len(rumors)})=\n<div style='column-count:3; column-gap:2em;'>\n"
        for rumor in rumors:
            tabber += f"{{{{Quote | {rumor} }}}}"
        tabber += "</div>\n"
    tabber += "</tabber>"
    return tabber


def generate_list(input_list: Iterable, html: bool = False):
    if html:
        out = "<ul>"
        out += "\n".join(f"<li>{x}</li>" for x in input_list)
        out += "</ul>"
        return out
    return "\n".join([f"* {x}" for x in input_list]).strip()


def faction_link(faction: fl.entities.universe.Faction) -> str:
    return f"[[File:{faction.nickname}.png|19px]] [[{faction.name()}]]"


def region_link(region: str) -> str:
    return (
        f"{{{{House Link | {region.title()} | long }}}}"
        if region in CONFIG["pageGen"]["houses"]
        else "Independent"
    )


def fade_out(stuff: str):
    return (
        """<div style="max-height: 500px; overflow-y: auto; -webkit-mask-image: linear-gradient(to bottom, black 90%, transparent 100%); mask-image: linear-gradient(to bottom, black 90%, transparent 100%); padding-bottom: 60px;">\n"""
        + stuff
        + "\n</div>"
    )


def ship_table(ships: fl.entities.EntitySet) -> str:
    return generate_table(
        ["Ship", "Class", "Price"],
        [
            (
                f"[[File:{ship.nickname}.png|19px]] [[{ship.name()}]]",
                ship.type(),
                ship.price(),
            )
            for ship in ships
        ],
        sortable=True,
    )


def base_table(bases: fl.entities.EntitySet) -> str:
    return generate_table(
        header=["Base", "Owner", "System", "Region"],
        entries=[
            (
                f"[[{base.name()}]]",
                faction_link(base.owner()),
                f"[[{base.system_().name()}]]",
                region_link(base.system_().region()),
            )
            for base in bases
        ],
        sortable=True,
    )


# ============== #


def generate_ship_page(ship: Ship) -> str:
    # techcompat = ship_entry.techcompat
    # max_wep = max(
    #     {
    #         int(re.findall("\\d+", nick)[-1])
    #         for nick, hardpoint in entry.hardpoints().items()
    #         if any(x.category() == "weapons" for x in hardpoint)
    #     }
    # )
    # max_shield = "{:,}".format(
    #     max(
    #         {
    #             max({int(re.findall("\\d+", x.name())[-1]) for x in hardpoint})
    #             for nick, hardpoint in entry.hardpoints().items()
    #             if "hpshield" in nick
    #         }
    #     )
    # )
    torpedo_count = len([x for x in ship.hardpoints() if "torpedo" in x.lower()])
    mine_count = len([x for x in ship.hardpoints() if "mine" in x.lower()])
    cm_count = len([x for x in ship.hardpoints() if "cm" in x.lower()])
    thruster_count = len([x for x in ship.hardpoints() if "thruster" in x.lower()])

    thruster_force = 72000
    engine = ship.engine()
    ship.linear_drag = (
        ship.linear_drag
        if not isinstance(ship.linear_drag, list)
        else ship.linear_drag[-1]
    )
    if engine:
        engine.linear_drag = (
            engine.linear_drag
            if not isinstance(engine.linear_drag, list)
            else engine.linear_drag[-1]
        )
    linear_drag = ship.linear_drag + engine.linear_drag if engine else ship.linear_drag
    force = thruster_force + engine.max_force if engine else thruster_force
    other = "<ul>"
    if torpedo_count > 0:
        other += f"<li> {torpedo_count}xCD/T</li>\n"
    if cm_count > 0:
        other += f"<li> {cm_count}xCM</li>\n"
    if mine_count > 0:
        other += f"<li> {mine_count}xM</li>\n"
    other += "</ul>"

    pob_recipes = ""
    if ship in get_pob_recipes_ships():
        pob_recipes = "=== Craftable in POB Recipes ===\n"
        recipes = set()
        for infotext, goods in get_pob_recipes().items():
            for good in goods:
                if isinstance(good, ShipPackage) and good.ship() == ship:
                    recipes.add(infotext)
        pob_recipes += generate_list(recipes)
        pob_recipes += "[[Category: Craftable]]"

    hardpoint_names = [
        x[-1].name()
        for x in ship.hardpoints().values()
        if x[-1].name() != x[-1].nickname
    ]
    engine.cruise_speed = (
        engine.cruise_speed
        if engine and not isinstance(engine.cruise_speed, list)
        else (engine.cruise_speed[-1] if engine else 0)
    )
    return load_template("ship").substitute(
        name=ship.infocard("plain").split("\n")[0],
        image=f"{ship.nickname}.png",
        tech_column=techcell(ship),
        ship_class=(ship.type()),
        gun_count=(len([x for x in ship.hardpoints() if "weapon" in x.lower()])),
        turret_count=(len([x for x in ship.hardpoints() if "turret" in x.lower()])),
        other=other,
        hull=("{:,}".format(ship.hit_pts)),
        cargo=("{:,}".format(ship.hold_size)),
        batteries=("{:,}".format(ship.shield_battery_limit)),
        bots=("{:,}".format(ship.nanobot_limit)),
        impulse=("{:,}".format(round(ship.impulse_speed(), 2))),
        turnrate=("{:,}".format(round(math.degrees(ship.turn_rate()), 2))),
        max_thrust=(
            int(force / linear_drag)
            if thruster_count > 0
            else '<span style="color: #f7001d; font-style: italic;">Thruster not available</span>'
        ),
        max_cruise=(
            "{:,}".format(
                engine.cruise_speed
                if engine and engine.cruise_speed != 0
                else fl.interface.get_constants()["engineequipconsts"]["cruising_speed"]
            )
        ),
        power_output=("{:,}".format(ship.power_core().capacity)),
        power_recharge=("{:,}".format(ship.power_core().charge_rate)),
        hull_price=("{:,}".format(ship.hull().price)) + "$",
        package_price=("{:,}".format(ship.price())) + "$",
        infocard=(ship.infocard().strip()),
        moors=not ship.mission_property == "can_use_berths",
        hardpoints=(
            generate_list(
                f"{hardpoint_names.count(n)}x {n}" for n in set(hardpoint_names)
            )
        ),
        includes=(
            generate_list(
                f'{equip.name()} (${"{:,}".format(equip.price())})'
                for equip in ship.equipment()
            )
        ),
        sold_at=base_table(filter_bases(ship.sold_at())),
        pob_recipes=pob_recipes,
        categories=f"[[Category: {ship.type()}]]",
    )


def generate_system_page(system: System) -> str:
    houses = CONFIG["pageGen"]["houses"]
    corps = CONFIG["pageGen"]["corporations"]

    suns = ""
    for star in system.stars():
        suns += f"'''{star.name()}'''\n"
        card = star.infocard("plain")
        card = card[:-1]
        card = card.split("\n")
        for x in card:
            suns += f"* {x}\n"

    bases: EntitySet[Base] = EntitySet()
    lawful_factions: EntitySet[Faction] = EntitySet()
    unlawful_factions: EntitySet[Faction] = EntitySet()
    corporate_factions: EntitySet[Faction] = EntitySet()

    for base in system.bases():
        if not isinstance(base, fl.entities.solars.PlanetaryBase):
            bases.add(base.universe_base())
        if base.owner() in corps:
            corporate_factions.add(base.owner())
        elif base.owner().legality() == "Lawful":
            lawful_factions.add(base.owner())
        elif base.owner().legality() == "Unlawful":
            unlawful_factions.add(base.owner())

    wrecks = "<div style='column-count:3; column-gap:2em;'>\n"
    for w in system.wrecks():
        if (
            "surprise" in w.nickname.lower()
            or "suprise" in w.nickname.lower()
            or "secret" in w.nickname.lower()
        ):
            wrecks += '<div style="break-inside: avoid; margin-bottom:1em;">\n'
            wrecks += f"=== {w.name()} - {w.sector()} ===\n{w.infocard('html')}\n"
            if w.loot():
                wrecks += """Contains:\n<ul style="margin-top:-15px;">\n"""
                for item, amount in w.loot().items():
                    wrecks += f"<li>{amount}x [[{item.name()}]]</li>\n"
                wrecks += "</ul>\n"
            wrecks += "</div>\n"
    wrecks += "</div>\n"

    return load_template("system").substitute(
        name=system.name(),
        nickname=system.nickname,
        infocard=system.infocard("html").split("Settled Planets")[0] + "</div>",
        government=region_link(system.region()),
        region=system.region().title(),
        neighbors=generate_list(
            [
                f"[[{x.name()}]]"
                for x in filter_systems(EntitySet(system.connections().values()))
            ],
            html=True,
        ),
        lawful_factions=generate_list(
            [faction_link(faction) for faction in lawful_factions]
        ),
        trade_factions=generate_list(
            [faction_link(faction) for faction in corporate_factions]
        ),
        unlawful_factions=generate_list(
            [faction_link(faction) for faction in unlawful_factions]
        ),
        suns=suns,
        planets=generate_table(
            header=["Planet", "Owner"],
            entries=[
                (
                    f"[[{x.name()}]]",
                    (
                        "Uninhabited"
                        if not isinstance(x, fl.entities.solars.PlanetaryBase)
                        else faction_link(x.owner())
                    ),
                )
                for x in system.planets()
            ],
        ),
        stations=generate_table(
            header=["Station", "Owner"],
            entries=[
                (f"[[{x.name()}]]", faction_link(x.owner()))
                for x in filter_bases(bases)
            ],
        ),
        fields=generate_list(
            [
                x.name()
                for x in system.zones()
                if x.name() and (x.asteroids() or x.nebulae())
            ]
        ),
        mining_zones=generate_list(
            [f"[[{c.name()}]]" for c in system.mineable_commodities()]
        ),
        navmap=f'[[File:{system.nickname}_map.png|center|750px|link={CONFIG["wikiGen"]["sysmapURL"]}#q={system.name().replace(" ", "%20")}]]',
        nebulae="<div style='column-count:3; column-gap:2em;'>\n"
        + "\n".join(
            [
                f"""<div style="break-inside: avoid; margin-bottom:1em;">\n=== {x.name()} ===\n{x.infocard('html')}\n</div>\n"""
                for x in system.zones()
                if x.nebulae()
            ]
        )
        + "</div>\n",
        asteroids="<div style='column-count:3; column-gap:2em;'>\n"
        + "\n".join(
            [
                f"""<div style="break-inside: avoid; margin-bottom:1em;">\n=== {x.name()} ===\n{x.infocard('html')}</div>\n"""
                for x in system.zones()
                if x.asteroids()
            ]
        )
        + "</div>\n",
        wrecks=wrecks,
        gates=generate_table(
            header=["Target System", "Type", "Location"],
            entries=[
                (f"[[{destination.name()}]]", jump.type(), jump.sector())
                for jump, destination in system.connections().items()
                if destination in filter_systems(system.connections().values())
            ],
        ),
    )


def generate_solar_page(solar: Solar):
    return load_template("solar").substitute(
        name=solar.name(),
        nickname=solar.nickname,
        system=solar.system().name(),
        region=region_link(solar.system().region()),
        region_=solar.system().region(),
        nearby=(
            l
            if (
                l := generate_list(
                    [
                        f"[[{x.name()}]]"
                        for x in solar.nearby(20_000)
                        if isinstance(x, BaseSolar)
                    ],
                    html=True,
                )
            )
            else "<i>None</i>"
        ),
        infocard=solar.infocard(),
    )


def generate_base_page(base: Base) -> str:
    bribes_missions = generate_table(
        ["", "Offers Missions", "Offers Bribes"],
        [
            (
                f"'''{faction_link(faction)}'''",
                "✔" if faction in base.missions() else "✗",
                "✔" if faction in base.bribes() else "✗",
            )
            for faction in base.missions() + base.bribes()
        ],
    )

    econ_content = []
    for commodity in EntitySet(base.buys_commodities().keys()) + EntitySet(
        base.sells_commodities().keys()
    ):
        sell = base.sells().get(commodity, commodity.price())
        buy = base.buys().get(commodity, commodity.price())
        good = commodity.good()
        sell_rating = (
            "-"
            if commodity.price() * good.bad_sell_price
            < sell
            < commodity.price() * good.good_sell_price
            else (
                "<span style='color:green'>↗</span>"
                if sell > commodity.price() * good.good_sell_price
                else "<span style='color:red'>↘</span>"
            )
        )
        buy_rating = (
            "-"
            if commodity.price() * good.bad_buy_price
            < buy
            < commodity.price() * good.good_buy_price
            else (
                "<span style='color:green'>↗</span>"
                if buy > commodity.price() * good.good_buy_price
                else "<span style='color:red'>↘</span>"
            )
        )
        sell = "$" + "{:,}".format(sell)
        buy = "$" + "{:,}".format(buy)
        if commodity not in base.sells_commodities():
            sell = "-"
            sell_rating = "-"
        if commodity not in base.buys_commodities():
            buy = "-"
            buy_rating = "-"
        econ_content.append(
            (f"[[{commodity.name()}]]", sell, buy, sell_rating, buy_rating)
        )

    economy = generate_table(
        [
            "Commodity",
            "Export Cost",
            "Import Cost",
            "Export Rating",
            "Import Rating",
        ],
        econ_content,
        sortable=True,
    )

    ships = ship_table(EntitySet(base.sells_ships().keys()))
    news = defaultdict(set)
    for new in base.news():
        candidates = re.findall(r"\[(.*?)]", new.headline_())
        year = ""
        if candidates:
            year = candidates[0]
        news[year].add(new)
    news = dict(sorted(news.items(), reverse=True))
    news_tabber = "<tabber>\n"
    for year, various_news in news.items():
        news_tabber += f"|-|{year} ({len(news[year])})=\n<div style='column-count:2; column-gap:2em;'>\n"
        for new in various_news:
            news_tabber += f"""<div class="mw-collapsible mw-collapsed" style="border-bottom:1px solid rgba(255,255,255,0.08); break-inside:avoid; margin-bottom:2px;"><div style="padding:4px 0; cursor:pointer;"><span style="color:rgba(255,255,255,0.35); margin-right:6px;">›</span>[[File:news_{new.icon}.png|21px]] <nowiki>{new.headline_().split("]", 1)[-1].strip()}</nowiki></div><div class="mw-collapsible-content" style="padding:6px 0 10px 20px; font-size:0.9em; color:rgba(255,255,255,0.85);"><span style="float:right; margin: 10px">[[File:logo_{new.logo if new.logo.lower() != "default" else "genericnews"}.png]]</span><nowiki>{new.text_()}</nowiki></div></div>\n"""
        news_tabber += "</div>\n"
    news_tabber += "</tabber>"

    other = f"[[Category: {base.owner().name()}]]\n[[Category: {base.system_().region()}]]\n[[Category: {base.system_().name()}]]\n"

    return load_template("base").substitute(
        name=base.name(),
        nickname=base.nickname,
        infocard=base.infocard(),
        owner=faction_link(base.owner()),
        location=f"{base.sector()}, [[{base.system_().name()}]]",
        bribes_missions=bribes_missions,
        economy=fade_out(economy),
        ships_sold=ships,
        news=news_tabber,
        rumors=rumor_tabber(base),
        other=other,
    )


def generate_faction_page(faction: Faction) -> str:
    repsheet = "{{Reputation_Table/Start|width=100%}}\n"
    for f in sorted(
        list(filter_factions(faction.rep_sheet().keys())),
        key=lambda x: faction.rep_sheet()[x],
    ):
        if not f:
            continue
        rep = faction.rep_sheet()[f]
        if rep == 0:
            continue
        rep = f"+{rep}" if rep > 0 else rep
        repsheet += f"{{{{RT|{faction_link(f)}|{rep}}}}}\n"
    repsheet += "{{Reputation_Table/End}}"

    return load_template("faction").substitute(
        name=faction.name(),
        nickname=faction.nickname,
        alignment=(
            "Corporation"
            if faction.name() in CONFIG["pageGen"]["corporations"]
            else faction.legality().title()
        ),
        infocard=faction.infocard(),
        ships=fade_out(ship_table(filter_ships(faction.ships()))),
        bases=fade_out(base_table(filter_bases(faction.bases()))),
        bribes=fade_out(base_table(filter_bases(faction.bribes()))),
        repsheet=fade_out(repsheet),
        rumors=rumor_tabber(faction),
    )


def generate_commodity_page(commodity: Commodity) -> str:
    mineable = ""
    if filter_systems(commodity.mineable_in()):
        mineable = "=== Mineable in Systems ===\n"
        mineable += generate_list(
            [f"[[{x.name()}]]" for x in filter_systems(commodity.mineable_in())]
        )
        mineable += "[[Category: Mineable]]"
    return load_template("commodity").substitute(
        name=commodity.name(),
        image_name=f"{icon_name(commodity.good().item_icon)}.png",
        cargo_space=commodity.volume,
        decay_rate=(
            f"{commodity.decay_per_second}/sec"
            if commodity.decay_per_second
            else "<i>no decay</i>"
        ),
        price=commodity.price(),
        infocard=commodity.infocard(),
        buy_bases=fade_out(
            generate_table(
                ["Base", "Owner", "System", "Region", "Price"],
                [
                    (
                        f"[[{base.name()}]]",
                        faction_link(base.owner()),
                        f"[[{base.system_().name()}]]",
                        base.system_().region(),
                        commodity.bought_at()[base],
                    )
                    for base in filter_bases(EntitySet(commodity.bought_at().keys()))
                ],
                title="Bases Buying",
                sortable=True,
            )
        ),
        sell_bases=fade_out(
            generate_table(
                ["Base", "Owner", "System", "Region", "Price"],
                [
                    (
                        f"[[{base.name()}]]",
                        faction_link(base.owner()),
                        f"[[{base.system_().name()}]]",
                        base.system_().region(),
                        commodity.sold_at()[base],
                    )
                    for base in filter_bases(EntitySet(commodity.sold_at().keys()))
                ],
                title="Bases Selling",
                sortable=True,
            )
        ),
        mineable_in=mineable,
    )


def generate_gun_page(gun: Gun) -> str:
    availability = "== Availability ==\n"
    if gun.sold_at():
        availability += f'=== Bases ===\n{generate_table(["Base", "Owner", "System", "Region", "Price"], [(f"[[{base.name()}]]", faction_link(base.owner()), f"[[{base.system_().name()}]]", base.system_().region(), gun.sold_at()[base]) for base in filter_bases(gun.sold_at().keys())])}'
    if gun.wrecks():
        availability += f'=== Wrecks ===\n{generate_table(["Name", "System", "Sector"], [(wreck.name(), f"[[{wreck.system().name()}]]", wreck.sector()) for wreck in gun.wrecks()])}'

    return load_template("gun").substitute(
        name=gun.name(),
        nickname=gun.nickname,
        technology=gun.technology(),
        hull_damage=gun.hull_damage(),
        shield_damage=gun.shield_damage(),
        hull_damage_s=gun.hull_dps(),
        shield_damage_s=gun.shield_dps(),
        refire=gun.refire(),
        energy_usage=gun.energy_per_second(),
        projectile_velocity=gun.muzzle_velocity,
        range=gun.range(),
        efficiency=gun.efficiency(),
        flstat_rating=gun.rating(),
        infocard=gun.infocard(),
        availability=availability,
        type=gun.hp_gun_type,
    )


def generate_special():
    ship_table_row = """|-\n|{name}\n|{faction}\n|{class}\n|style="text-align: center;"|{guns}\n|style="text-align: center;"|{turrets}\n|style="text-align: center;"|{mines} \n|style="text-align: center;"|{cds}\n|style="text-align: center;"|{cms}\n|style="text-align: center;"|{turnrate}\n|style="text-align: center;"|{hitpoints}\n|style="text-align: center;"|{powercore}\n|style="text-align: center;"|{bots}\n|style="text-align: center;"|{bats}\n|style="text-align: center;"|{cargo} \n|style="text-align: center;"|{price}"""

    pages = {}

    ship_table = """{| class="sortable wikitable mw-collapsible mw-collapsed" width="100%"\n|+ \n|-\n!rowspan="2" style="text-align: center;"|Name\n!rowspan="2" style="text-align: center;"|Techcell\n!rowspan="2" style="text-align: center;"|Class\n!rowspan="1" style="text-align: center;"|Guns\n!rowspan="1" style="text-align: center;"|Turrets\n!rowspan="1" style="text-align: center;"|Mines\n!rowspan="1" style="text-align: center;"|CDs/Ts\n!rowspan="1" style="text-align: center;"|CMs\n!rowspan="2" style="text-align: center;"|Turn<br>Rate\n!rowspan="2" style="text-align: center;"|Hit<br>Points\n!rowspan="2" style="text-align: center;"|Power<br>Core\n!rowspan="2" style="text-align: center;"|Nanobots\n!rowspan="2" style="text-align: center;"|Shield Batteries\n!rowspan="2" style="text-align: center;"|Hold<br>Size\n!rowspan="2" style="text-align: center;"|Package<br>Price\n|-\n!colspan="6" style="text-align: center;"|Hardpoint Types\n"""
    for ship in filter_ships(fl.get_ships()):
        ship_table += f"\n{ship_table_row}"

        ship_table = ship_table.replace("{name}", f"[[{ship.name()}]]")
        ship_table = ship_table.replace("{class}", ship.type())
        ship_table = ship_table.replace("{faction}", techcell(ship))
        ship_table = ship_table.replace(
            "{guns}", str(len([x for x in ship.hardpoints() if "weapon" in x.lower()]))
        )
        ship_table = ship_table.replace(
            "{turrets}",
            str(len([x for x in ship.hardpoints() if "turret" in x.lower()])),
        )
        ship_table = ship_table.replace(
            "{mines}", str(len([x for x in ship.hardpoints() if "mine" in x.lower()]))
        )
        ship_table = ship_table.replace(
            "{cds}", str(len([x for x in ship.hardpoints() if "torpedo" in x.lower()]))
        )
        ship_table = ship_table.replace(
            "{cms}", str(len([x for x in ship.hardpoints() if "cm" in x.lower()]))
        )
        ship_table = ship_table.replace(
            "{turnrate}", str("{:,}".format(round(math.degrees(ship.turn_rate()), 2)))
        )
        ship_table = ship_table.replace("{hitpoints}", "{:,}".format(ship.hit_pts))
        ship_table = ship_table.replace(
            "{powercore}", "{:,}".format(ship.power_core().capacity)
        )
        ship_table = ship_table.replace("{bots}", "{:,}".format(ship.nanobot_limit))
        ship_table = ship_table.replace(
            "{bats}", "{:,}".format(ship.shield_battery_limit)
        )
        ship_table = ship_table.replace("{cargo}", "{:,}".format(ship.hold_size))
        ship_table = ship_table.replace("{price}", "$" + "{:,}".format(ship.price()))
    ship_table += "|}\n<hr>"
    pages["Category:Ships"] = load_template("special_ship").substitute(table=ship_table)

    pages["Category:Commodities"] = load_template("special_commodity").substitute(
        table=generate_table(
            [
                "Commodity",
                "Volume",
                "Decay Rate <br />",
                "Default Price",
                "Mined in",
            ],
            [
                (
                    f"[[{c.name()}]]",
                    c.volume,
                    (
                        f"{c.decay_per_second}/sec"
                        if c.decay_per_second
                        else "<i>no decay</i>"
                    ),
                    c.price(),
                    generate_list(
                        (f"[[{s.name()}]]" for s in filter_systems(c.mineable_in())),
                        html=True,
                    ),
                )
                for c in filter_commodities(fl.get_commodities())
            ],
            sortable=True,
            style="width: 100%",
        )
    )

    return pages


def load_all_infocards():  # probably extremely inefficient, since loading just one resource from each dll should be enough, but w/e
    for i in range(65539 * len(fl.paths.dlls)):
        dll.lookup(i)


def apply_server_infocard_override():
    load_all_infocards()

    infocards = dict(
        fl.formats.ini.parse(
            "./server_config/infocard_overrides.cfg", discovery_config=True
        )
    ).get("IDStrings")

    for id, value in infocards.items():
        dll.override_resource(int(id), value)

    # verify things worked
    for id, value in infocards.items():
        assert dll.lookup(int(id)) == value


@lru_cache
def get_pob_recipes() -> dict[str, EntitySet[Good]]:
    recipes = fl.formats.ini.parse(
        "./server_config/base_recipe_items.cfg", discovery_config=True
    )
    result = defaultdict(EntitySet)
    for section_name, attributes in recipes:
        if section_name != "recipe":
            continue

        attributes["produced_item"] = (
            items
            if isinstance((items := attributes["produced_item"]), list)
            else [items]
        )
        for beans in attributes["produced_item"]:
            beans = beans.split(",")[0].strip()
            good: Good = fl.get_goods().get(beans)
            if good:
                result[attributes["infotext"]].add(good)
    return result


@lru_cache
def get_pob_recipes_ships() -> EntitySet[Ship]:
    recipes = get_pob_recipes()
    result = EntitySet()
    for infotext, items in recipes.items():
        for item in items:
            if isinstance(item, ShipPackage):
                result.add(item.ship())
    return result


@lru_cache
def techcell(entity: Entity) -> str:
    techcells = fl.formats.ini.parse(
        "./server_config/techcompat.cfg", discovery_config=True
    )
    for section_name, attributes in techcells:
        if section_name != "tech":
            continue
        if entity.nickname in attributes.get("item"):
            return attributes.get("name", "")
    return ""


def assemble_pages():
    sources = {}
    redirects = {}

    print("Assembling pages\n===================")

    sys_source = {}
    print("Assembling System pages")
    for i, system in enumerate(s := filter_systems(fl.get_systems())):
        print(
            f"{i+1}/{len(s)}: {system.nickname}                                     ",
            end="\r",
        )
        source = generate_system_page(system=system) + "[[Category: NukeOnPatch]]"
        sys_source[system.name()] = source
    sources["Systems"] = sys_source
    print("")

    solar_source = {}
    print("Assembling Solar pages")
    for i, solar in enumerate(
        s := [
            x
            for x in EntitySet.merge(
                s.planets() for s in filter_systems(fl.get_systems())
            )
            if not isinstance(x, fl.entities.PlanetaryBase)
        ]
    ):
        print(
            f"{i+1}/{len(s)}: {solar.nickname}                                     ",
            end="\r",
        )
        source = generate_solar_page(solar=solar) + "[[Category: NukeOnPatch]]"
        solar_source[solar.name()] = source
    sources["Solars"] = solar_source
    print("")

    ship_source = {}
    print("Assembling Ship pages")
    for i, ship in enumerate(s := filter_ships(fl.get_ships())):
        print(
            f"{i+1}/{len(s)}: {ship.nickname}                                     ",
            end="\r",
        )
        source = generate_ship_page(ship=ship) + "[[Category: NukeOnPatch]]"
        ship_source[ship.name()] = source
        long_name = ship.infocard("plain").split("\n")[0]
        if ship.name() != long_name:
            redirects[long_name] = (
                f"""#REDIRECT[[{ship.name()}]] [[Category: NukeOnPatch]]"""
            )
    sources["Ships"] = ship_source
    print("")

    base_source = {}
    print("Assembling Base pages")
    for i, base in enumerate(b := filter_bases(fl.get_bases())):
        print(
            f"{i+1}/{len(b)}: {base.nickname}                                     ",
            end="\r",
        )
        source = generate_base_page(base=base) + "[[Category: NukeOnPatch]]"
        unique_name = (
            base.name()
            if base.name() not in sources["Ships"].keys()
            else f"{base.name()} (b)"
        )
        base_source[unique_name] = source
    sources["Bases"] = base_source
    print("")

    faction_source = {}
    print("Assembling Faction pages")
    for i, faction in enumerate(f := filter_factions(fl.get_factions())):
        print(
            f"{i+1}/{len(f)}: {faction.nickname}                                     ",
            end="\r",
        )
        source = generate_faction_page(faction=faction) + "[[Category: NukeOnPatch]]"
        faction_source[faction.name()] = source
        if faction.name() != faction.short_name():
            redirects[faction.short_name()] = (
                f"""#REDIRECT[[{faction.name()}]] [[Category: NukeOnPatch]]"""
            )
    sources["Factions"] = faction_source
    print("")

    commodity_source = {}
    print("Assembling Commodity pages")
    for i, commodity in enumerate(c := filter_commodities(fl.get_commodities())):
        print(
            f"{i+1}/{len(c)}: {commodity.nickname}                                     ",
            end="\r",
        )
        source = (
            generate_commodity_page(commodity=commodity) + "[[Category: NukeOnPatch]]"
        )
        commodity_source[commodity.name()] = source
    sources["Commodities"] = commodity_source
    print("")

    weapon_source = {}
    print("Assembling Gun pages")
    for i, gun in enumerate(g := fl.get_equipment().of_type(Gun)):
        print(
            f"{i+1}/{len(g)}: {gun.nickname}                                     ",
            end="\r",
        )
        source = generate_gun_page(gun=gun) + "[[Category: NukeOnPatch]]"
        weapon_source[gun.name()] = source
    sources["Weapons"] = weapon_source
    print("")

    print("Assembling Redirect pages")
    sources["Redirects"] = redirects

    print("Assembling Special pages")
    sources["Special"] = generate_special()

    return sources


def main():
    secret = load_data("secret.json")
    fl.set_install_path(secret["freelancer"])
    sources = assemble_pages()
    print("DONE")
    return sources
