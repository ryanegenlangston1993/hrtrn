import requests
import discord

import datetime
from decimal import Decimal
import re

import dbutils


def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def num_to_text(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def text_to_num(text):
    text = text.upper().replace(",", "")
    numbers = re.sub(f'[a-z]', '', text.lower())

    if "K" in text:
        return Decimal(numbers) * 1000
    elif "M" in text:
        return Decimal(numbers) * 1000000
    elif "B" in text:
        return Decimal(numbers) * 1000000000
    else:
        return Decimal(numbers)


def check_admin(member):
    return True if member.guild_permissions.administrator else False


def remove_torn_id(name):
    return re.sub("[[].*?[]]", "", name)[:-1]


def get_torn_id(name):
    return re.compile(r"\[(\d+)\]").findall(name)[0]


def log(message, file):
    file.write(str(datetime.datetime.now()) + " -- " + message + "\n")
    file.flush()


def commas(number):
    return "{:,}".format(number)


def get_prefix(bot, message):
    for guild in dbutils.read("guilds")["guilds"]:
        if guild["id"] == str(message.guild.id):
            return guild["prefix"]


async def tornget(ctx, url, guildkey=1, key=None, random=False):
    if random:
        raise NotImplementedError()

    if key is not None:
        apikey = key
    elif guildkey == 1:
        apikey = dbutils.get_guild(ctx.guild.id, "tornapikey")
    elif guildkey == 2:
        apikey = dbutils.get_guild(ctx.guild.id, "tornapikey2")
    else:
        raise ValueError()

    request = requests.get(f'{url}{apikey}')

    if request.status_code != 200:
        embed = discord.Embed()
        embed.title = "Error"
        embed.description = f'Something has possibly gone wrong with the request to the Torn API with ' \
                            f'HTTP status code {request.status_code} has been given at ' \
                            f'{datetime.datetime.now()}.'
        await ctx.send(embed=embed)
        log(f'The Torn API (Key {guildkey}) has responded with HTTP status code {request.status_code}.',
            open("log.txt", "a"))
        return Exception

    if 'error' in request.json():
        error = request.json()['error']
        embed = discord.Embed()
        embed.title = "Error"
        embed.description = f'Something has gone wrong with the request to the Torn API with error code ' \
                            f'{error["code"]} ({error["error"]}). Visit the [Torn API documentation]' \
                            f'(https://api.torn.com/) to see why the error was raised.'
        await ctx.send(embed=embed)
        log(f'The Torn API (Key {guildkey}) has responded with error code {error["code"]}.', open("log.txt", "a"))
        raise Exception

    return request.json()
