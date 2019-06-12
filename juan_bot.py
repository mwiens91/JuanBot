#!/usr/bin/env python3

import json
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

token = config["client-token"]
juan_name = config["juan-name"]
juan_discriminator = config["juan-discriminator"]

# Unpack previous record
record_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "typing_record.json"
)

try:
    with open(record_path, "r") as record_file:
        record_dict = json.load(record_file)

except IOError:
    # No previous record set
    record_dict = {"time": 0, "date": None}

    with open(record_path, "w") as record_file:
        json.dump(record_dict, record_file)

# Start the bot client
client = discord.Client()

# Bot events
@client.event
async def on_ready():
    print("Successfully logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    if (
        message.author.name == juan_name
        and message.author.discriminator == juan_discriminator
    ):
        await message.channel.send("stop")


# Run the bot
client.run(token)
