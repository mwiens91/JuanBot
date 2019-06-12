#!/usr/bin/env python3

import os
import sys
import discord
import yaml


# Parse config file
config_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "config.yaml"
)

try:
    with open(config_path, "r") as config_file:
        config = yaml.safe_load(config_file)
except IOError:
    print("Config file not found!")
    sys.exit(1)

token = config["token"]


# DEBUG
print(token)
