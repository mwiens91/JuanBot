#!/usr/bin/env python3

import datetime
import os
import pickle
import random
import sys
import discord
import pytz
import yaml

# Constants
GRACE_PERIOD_SECONDS = 45
STOP_MESSAGE_SECONDS = 30
STOP_MESSAGE_INCREMENT_SECONDS = 15

# Stop messages (this is going to be mutable)
stop_messages = [
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


# Parse previous record from file
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

# Typing tracking state variables
juan_is_typing = False
juan_is_typing_start = None
juan_is_typing_last = None
messages_sent = 0

# Helper functions
def user_is_juan(username, discriminator):
    return username == juan_name and discriminator == juan_discriminator


def set_state_vars():
    global juan_is_typing, juan_is_typing_start, juan_is_typing_last

    juan_is_typing = True
    juan_is_typing_start = current_datetime
    juan_is_typing_last = current_datetime


def unset_state_vars():
    global juan_is_typing, juan_is_typing_start, juan_is_typing_last, messages_sent

    juan_is_typing = False
    juan_is_typing_start = None
    juan_is_typing_last = None
    messages_sent = 0


def increment_messages_sent():
    global messages_sent

    messages_sent += 1


def update_last_typed():
    global juan_is_typing_last

    juan_is_typing_last = datetime.datetime.now(timezone)


def update_record_dict(timedelta):
    global record_dict

    record_dict["datetime"] = datetime.datetime.now()
    record_dict["timedelta"] = timedelta

    with open(record_path, "wb") as record_file:
        pickle.dump(record_dict, record_file, protocol=pickle.HIGHEST_PROTOCOL)


# Bot events
@client.event
async def on_ready():
    print("Successfully logged in as %s" % client.user)


@client.event
async def on_typing(channel, user, _):
    if user_is_juan(user.name, user.discriminator):
        current_datetime = datetime.datetime.now(timezone)

        # If Juan typed prior to the last GRACE_PERIOD_SECONDS but
        # didn't send a message, reset state variables
        if (
            juan_is_typing
            and juan_is_typing_last - current_datetime
            > datetime.timedelta(seconds=GRACE_PERIOD_SECONDS)
        ):
            unset_state_vars()

        if not juan_is_typing:
            # Juan just started typing
            set_state_vars()
        else:
            # Record that this is the latest time Juan started typing
            update_last_typed()

            # Juan is currently typing. Randomly tell him to stop if
            # he's typing for >= STOP_MESSAGE_SECONDS and every
            # STOP_MESSAGE_INCREMENT_SECONDS after that.
            if current_datetime - juan_is_typing_start >= datetime.timedelta(
                seconds=STOP_MESSAGE_SECONDS
                + STOP_MESSAGE_INCREMENT_SECONDS * messages_sent
            ):
                # Randomly decide whether to send a message or not
                if random.choice([True] * 1 + [False] * 9):
                    increment_messages_sent()
                    await channel.send(random.choice(stop_messages))


@client.event
async def on_message(message):
    if juan_is_typing and user_is_juan(
        message.author.name, message.author.discriminator
    ):
        current_datetime = datetime.datetime.now(timezone)

        # Record the typing time
        typing_timedelta = current_datetime - juan_is_typing_start

        # Reset state variables
        unset_state_vars()

        if typing_timedelta > record_dict["timedelta"]:
            # Save this time
            update_record_dict(typing_timedelta)

            # Send a message about the new typing record
            await message.channel.send(
                '%s just set a new "**%s** is typing..." record!!! %.2f seconds!'
                % (juan_name, juan_name, typing_timedelta.total_seconds())
            )


# Run the bot
client.run(token)
