#!/usr/bin/env python3

import datetime
import os
import pickle
import random
import sys
import discord
import pytz
import yaml


# "Stop" message variations
STOP_MESSAGES = [
    "Stop.",
    "Uh oh.",
    "Incoming.",
    "Get ready.",
    "Here we go ...",
    "-_-",
    "Plz no.",
]

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
juan_is_typing_last = None
messages_sent = 0


@client.event
async def on_typing(channel, user, _):
    global juan_is_typing, juan_is_typing_start, juan_is_typing_last, messages_sent, timezone

    if user.name == juan_name and user.discriminator == juan_discriminator:
        current_datetime = datetime.datetime.now(timezone)

        # If Juan typed prior to the last 45 seconds but didn't send a
        # message, reset state variables
        if (
            juan_is_typing
            and juan_is_typing_last - current_datetime
            > datetime.timedelta(seconds=45)
        ):
            juan_is_typing = False

        if not juan_is_typing:
            # Juan just started typing
            juan_is_typing = True
            juan_is_typing_start = current_datetime
            juan_is_typing_last = current_datetime
        else:
            # Record that this is the latest time Juan started typing
            juan_is_typing_last = current_datetime

            # Juan is currently typing. Randomly tell him to stop if
            # he's typing for >= 30 seconds and every 15 seconds after
            # that.
            if random.choice(
                [True, False, False, False, False, False, False, False]
            ) and current_datetime - juan_is_typing_start >= datetime.timedelta(
                seconds=30 + 15 * messages_sent
            ):
                messages_sent += 1
                await channel.send(random.choice(STOP_MESSAGES))


@client.event
async def on_message(message):
    global record_dict, juan_is_typing, juan_is_typing_start, juan_is_typing_last, messages_sent

    if (
        juan_is_typing
        and message.author.name == juan_name
        and message.author.discriminator == juan_discriminator
    ):
        current_datetime = datetime.datetime.now(timezone)

        # Record the typing time
        typing_timedelta = current_datetime - juan_is_typing_start

        # Reset state variables
        juan_is_typing = False
        messages_sent = 0

        if typing_timedelta > record_dict["timedelta"]:
            # Save this time
            record_dict["datetime"] = current_datetime
            record_dict["timedelta"] = typing_timedelta

            with open(record_path, "wb") as record_file:
                pickle.dump(
                    record_dict, record_file, protocol=pickle.HIGHEST_PROTOCOL
                )

            # Send a message about the new typing record
            await message.channel.send(
                '%s just set a new "**%s** is typing..." record!!! %.2f seconds!'
                % (juan_name, juan_name, typing_timedelta.total_seconds())
            )


# Run the bot
client.run(token)
