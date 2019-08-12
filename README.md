# JuanBot

> Definition: A **Juan** is a Discord user who types for a long time but
> sends only short, questionable messages.

JuanBot is a Discord bot who tracks typing records for Juans and
occasionally cheerleads them when they're in the middle of typing for a
really long time.

## Setup

### Requirements

Use the Python 3 version of pip to install requirements from [the requirements file](requirements.txt).

### Configuration

You're going to need to fill in a few requirements specific to yourself
and the Juan you are targeting. First of all, make a copy of the
[example config file](config.yaml.example) as follows:

```
cp config.yaml.example config.yaml
```

Fill in the appropriate settings in the `config.yaml` file you just
created: `client-id` and `client-token` are going to come from the
Discord bot account you set up (go
[here](https://discordapp.com/developers/applications) to do that); the
`*-name` and `*-discriminator` settings refer to the respective username
and discriminator associated with the respective Discord user (the
discriminator is the number that appears beside a Discord user's
username when looking up their profile).

### Running it

Run the [main script](juan_bot.py) with

```
./juan_bot.py
```

## Commands

The main command (the rest are secret :smirk:) you want to use to
retreive typing records of the Juan is

```
@JuanBot pb
```

where you can replace `JuanBot` with whatever the username of the bot
you've setup is.
