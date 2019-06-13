#!/usr/bin/env python3

import datetime
import os
import pickle
import sys
import discord
import pytz
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
timezone = pytz.timezone(config["timezone"])


# Unpack previous record
record_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "typing_record.pickle"
)

try:
    with open(record_path, "rb") as record_file:
        record_dict = pickle.load(record_file)
except IOError:
    # No previous record set
    record_dict = {"timedelta": datetime.timedelta(0), "datetime": None}

    with open(record_path, "wb") as record_file:
        pickle.dump(record_dict, record_file, protocol=pickle.HIGHEST_PROTOCOL)

# Start the bot client
client = discord.Client()

# Startup message
@client.event
async def on_ready():
    print("Successfully logged in as %s" % client.user)


# "Juan is typing" tracking
juan_is_typing = False
juan_is_typing_start = None
messages_sent = 0


@client.event
async def on_typing(channel, user, _):
    global juan_is_typing, juan_is_typing_start, messages_sent

    if user.name == juan_name and user.discriminator == juan_discriminator:
        if not juan_is_typing:
            # Juan just started typing
            juan_is_typing = True
            juan_is_typing_start = datetime.datetime.now(timezone)
            messages_sent = 0
        else:
            # Juan is currently typing. Tell him to stop if he's typing
            # for >= 30 seconds and every 15 seconds after that.
            if datetime.datetime.now(
                timezone
            ) - juan_is_typing_start >= datetime.timedelta(
                seconds=30 + 15 * messages_sent
            ):
                messages_sent += 1
                await channel.send("stop")


# Run the bot
client.run(token)
