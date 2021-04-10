import json

jsons = ["guilds", "vault", "users", "requests", "armory"]


def _read(file):
    with open(f'{file}.json') as file:
        return json.load(file)


def _write(file, data):
    with open(f'{file}.json', 'w') as file:
        json.dump(data, file, indent=4)


def initialize():
    try:
        file = open("guilds.json")
        file.close()
    except FileNotFoundError:
        bottoken = input("Please input the bot token: ")
        data = {
            "bottoken": bottoken,
            "masterapikey": "",
            "superuser": 0,
            "prefix": "?",
            "guilds": []
        }
        _write("guilds", data)

    try:
        file = open("vault.json")
        file.close()
    except FileNotFoundError:
        _write("vault", {})

    try:
        file = open("users.json")
        file.close()
    except FileNotFoundError:
        _write("users", {})

    try:
        file = open("requests.json")
        file.close()
    except FileNotFoundError:
        data = {
            "nextrequest": 0
        }
        _write("requests", data)

    try:
        file = open("armory.json")
        file.close()
    except FileNotFoundError:
        _write("armory", {})


def read(file):
    if file in jsons:
        return _read(file)
    else:
        raise ValueError("Illegal File Name")


def write(file, data):
    if file in jsons:
        _write(file, data)
    else:
        raise ValueError("Illegal File Name")


def get_guild(guildid, key=None):
    for guild in read("guilds")["guilds"]:
        if str(guild["id"]) == str(guildid):
            if key is None:
                return guild
            else:
                return guild[key]


def get_vault(guildid, key=None):
    return read("vault")[str(guildid)] if key is None else read("vault")[str(guildid)][key]


def get_superuser():
    return read("guilds")["superuser"]


def get_user(id, key=None):
    return read("users")[str(id)] if key is None else read("users")[str(id)][key]
