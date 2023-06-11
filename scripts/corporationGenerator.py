import json
import flint as fl
from pprint import pprint

with open("secret.json", "r") as f:
    path = json.load(f)["freelancerPath"]
with open("config.json", "r") as f:
    config = json.load(f)

fl.set_install_path(path)

results = []
for faction in fl.factions:
    if faction.nickname not in faction.name() and not faction.name().isspace():
        if 'y' in input(f"Is this faction a corporation or guild?: {faction.name()}\ny/n"):
            results.append(faction.name())

pprint(results)
config["pageGen"]["corporations"] = results

with open("config.json", "w") as f:
    json.dump(config, f)