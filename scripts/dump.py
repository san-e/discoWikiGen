import json
import os
import subprocess
import time
from io import BytesIO
from pathlib import PureWindowsPath
from pageGen import filter_systems

from PIL import Image
from flint.formats import utf
from flint.paths import construct_path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

os.chdir(os.path.dirname(os.path.abspath(__file__)))
import flint as fl


def dump_models() -> None:
    print("== Dumping models ==")
    with open("./secret.json", "r") as f:
        secret = json.load(f)

    processes = set()
    MAX_PROCESSES = 50
    LLEDITSCRIPT = secret["librelancer"] + "/lleditscript"
    EXPORTER = "./exporter.cs-script"
    for i, ship in enumerate(fl.ships):
        print(f"{i}/{len(fl.ships)}: {ship.nickname}              ", end="\r")
        if len(processes) > MAX_PROCESSES:
            for process in processes:
                process.wait()
            processes.clear()
        arguments = [LLEDITSCRIPT, EXPORTER, ship.model()]
        for material in ship.materials():
            arguments.append(material)
        arguments.append(f"../dumpedData/models/ships/{ship.nickname}.glb")
        p = subprocess.Popen(arguments, stdout=subprocess.DEVNULL)
        processes.add(p)


def render_ships() -> None:
    print("== Rendering ships ==")
    with open("./secret.json", "r") as f:
        secret = json.load(f)

    LLEDITSCRIPT = secret["librelancer"] + "/lleditscript"
    RENDERER = "./render.cs-script"
    p = subprocess.Popen(
        (
            LLEDITSCRIPT,
            RENDERER,
            secret["freelancer"],
            "../dumpedData/images/ships",
        ),
    )
    p.wait()

    # crop transparency
    for image in os.listdir("../dumpedData/images/ships"):
        if not image.endswith(".png"):
            continue
        im = Image.open(f"../dumpedData/images/ships/{image}")
        im = im.crop(im.getbbox())
        im.save(f"../dumpedData/images/ships/{image}")


def dump_sysmaps():
    print("== Dumping Sysmaps ==")
    with open("./config.json", "r") as f:
        config = json.load(f)
    with open("./secret.json", "r") as f:
        secret = json.load(f)
    # == Setup ==
    options = Options()
    options.binary_location = secret["firefox"]
    options.add_argument("-headless")
    options.set_preference("layout.css.devPixelsPerPx", "2.0")
    service = Service(secret["webdriver"])
    driver = webdriver.Firefox(options=options, service=service)
    driver.set_window_size(1920, 1080)
    driver.get(config["wikiGen"]["sysmapURL"])

    n = len(fl.systems) - len(config["wikiGen"]["oorpSystems"])
    i = 1
    for system in filter_systems(fl.systems):
        if system.nickname in config["wikiGen"]["oorpSystems"]:
            continue
        print(f"{i}/{n}: {system.nickname}              ", end="\r", flush=True)
        i += 1
        driver.get(f"{config['wikiGen']['sysmapURL']}#q={system.name()}")
        driver.execute_script("location.reload(true);")
        time.sleep(1)
        x = 0
        # wait for system to load, reload the page if it doesn't
        while (
            driver.find_elements(By.CLASS_NAME, "loadingOverlay")
            or driver.find_elements(By.CLASS_NAME, "loaderTitle")
            or "Sirius" in {x.text for x in driver.find_elements(By.CLASS_NAME, "systemTitle")}
        ):
            time.sleep(0.1)
            x += 1
            if x >= 100:
                driver.execute_script("location.reload(true);")
                x = 0
        # wait for map to load, again
        timeout = 10
        while True:
            elements = driver.find_elements(By.CLASS_NAME, "systemTitle")
            if elements and elements[0].get_attribute("innerHTML") == system.name():
                break
            driver.execute_script("location.reload(true);")
            time.sleep(2)
            timeout -= 1
            if timeout <= 0:
                break
        sysmap = driver.find_elements(By.CLASS_NAME, "map")[0]
        sysmap.screenshot(f"../dumpedData/images/systems/{system.nickname}_map.png")
    print("")


def dump_icons():
    def icon_name(path):
        return os.path.splitext(PureWindowsPath(path).parts[-1])[0]

    def save_icon(icon, name, folder):
        if isinstance(icon, Image.Image):
            image = icon
        else:
            image = Image.open(BytesIO(icon))
        image.save(f"../dumpedData/images/{folder}/{name}.png")

    for commodity in fl.get_commodities():
        name = icon_name(commodity.good().item_icon) if commodity.good().item_icon else icon_name(commodity.good().DEFAULT_ICON)
        save_icon(
            commodity.icon(), name, "commodities"
        )

    # News Icons should be uploaded manually since they're hardcoded anyway

    news_logos = {}
    logo_name = None
    # we do some parsing fuckery here because the flint utf parser is quite barebones
    for name, data in utf.parse(
        construct_path("DATA/INTERFACE/NEURONET/NEWSVENDOR/newsvendor.txm")
    ):
        if "news" in name.lower():
            logo_name = name
        elif (name == "MIP0" or name == "MIPS") and data:
            news_logos[logo_name] = data

    for logo_name, data in news_logos.items():
        image = Image.open(BytesIO(data))
        image = image.crop((0, image.height * 0.125, image.width, image.height * 0.875))
        save_icon(image, f"logo_{logo_name}", "news")


def dump(
    models: bool = False,
    ship_render: bool = False,
    sysmaps: bool = False,
    icons: bool = False,
) -> None:
    if not fl.install_path_set():
        with open("./secret.json", "r") as f:
            secret = json.load(f)
        fl.set_install_path(secret["freelancer"])
    if models:
        dump_models()
    if ship_render:
        render_ships()
    if sysmaps:
        dump_sysmaps()
    if icons:
        dump_icons()


if __name__ == "__main__":
    dump(models=True, ship_render=False, sysmaps=False)
