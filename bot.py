import discord, asyncio, os, platform, sys
from discord.ext.commands import Bot
from discord.ext import commands
import dbutils

if not os.path.isfile("config.py"):
	sys.exit("'config.py' not found! Please add it and try again.")
else:
	import config

dbutils.initialize()

guilds = dbutils.read("guilds")
vaults = dbutils.read("vault")
users = dbutils.read("users")
aractions = dbutils.read("armory")

intents = discord.Intents.all()

bot = Bot(command_prefix=config.BOT_PREFIX, intents=intents)

@bot.event
async def on_ready():
  guild_count = 0

  for guild in bot.guilds:
    print(f"- {guild.id} (name: {guild.name})")
    guild_count +=1

    for jsonguild in guilds["guilds"]:
      if jsonguild["id"] == str(guild.id):
        break

    else:
      guilds["guilds"].append({
        "id": str(guild.id),
        "prefix": "?",
        "tornapikey": "",
        "tornapikey": ""
      })
      dbutils.write("guilds", guilds)

    if str(guild.id) not in vaults:
      vaults[guild.id] = {
        "channel": "",
        "role": "",
        "channel2": "",
        "role2": "",
        "banking": "",
        "banking2": ""
      }
      dbutils.write("vault", vaults)

    if str(guild.id) not in aractions:
      aractions[guild.id] = {
        "lastscan": 0,
        "requests": []
      }
      dbutils.write("armory", aractions)

    for member in guild.members:
      if str(member.id) in users:
        continue
      if member.bot:
        continue
      users[member.id] = {
        "tornid": "",
        "tornapikey": "",
        "generaluse": False
      }
      dbutils.write("users", users)

  bot.loop.create_task(status_task())
  print(f"Logged in as {bot.user.name}")
  print(f"Discord.py API version: {discord.__version__}")
  print(f"Python version: {platform.python_version()}")
  print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
  print("-------------------")

async def status_task():
	while True:
		await bot.change_presence(activity=discord.Game("with you!"))
		await asyncio.sleep(60)
		await bot.change_presence(activity=discord.Game("with Ryanthehoof and Helium!"))
		await asyncio.sleep(60)
		await bot.change_presence(activity=discord.Game(f"{config.BOT_PREFIX} help"))
		await asyncio.sleep(60)
		await bot.change_presence(activity=discord.Game("with humans!"))
		await asyncio.sleep(60)

bot.remove_command("help")

if __name__ == "__main__":
	for file in os.listdir("./cogs"):
		if file.endswith(".py"):
			extension = file[:-3]
			try:
				bot.load_extension(f"cogs.{extension}")
				print(f"Loaded extension '{extension}'")
			except Exception as e:
				exception = f"{type(e).__name__}: {e}"
				print(f"Failed to load extension {extension}\n{exception}")

@bot.event
async def on_message(message):

	if message.author == bot.user or message.author.bot:
		return

	if message.author.id in config.BLACKLIST:
		return
	await bot.process_commands(message)


@bot.event
async def on_command_completion(ctx):
	fullCommandName = ctx.command.qualified_name
	split = fullCommandName.split(" ")
	executedCommand = str(split[0])
	print(f"Executed {executedCommand} command in {ctx.guild.name} (ID: {ctx.message.guild.id}) by {ctx.message.author} (ID: {ctx.message.author.id})")

@bot.event
async def on_command_error(context, error):
	if isinstance(error, commands.CommandOnCooldown):
		embed = discord.Embed(
			title="Error!",
			description="This command is on a %.2fs cool down" % error.retry_after,
			color=config.error
		)
		await context.send(embed=embed)
	raise error

@bot.event
async def on_guild_join(guild):
    embed = discord.Embed()
    embed.title = f'Welcome to {bot.user.display_name}'
    embed.description = f'Thank you for inviting {bot.user.display_name} to your server'
    embed.add_field(name="Help", value="`?help` or contact <@tiksan#9110> on Discord, on tiksan [2383326] on Torn,"
                                       " or dssecret on Github")
    embed.add_field(name="How to Setup", value="Run admin commands that can be found in the [Wiki]"
                                               "(https://github.com/dssecret/torn-bot/wiki) under [Commands]"
                                               "(https://github.com/dssecret/torn-bot/wiki/Commands).")
    await guild.text_channels[0].send(embed=embed)

    for jsonguild in guilds["guilds"]:
        if jsonguild["id"] == str(guild.id):
            break
    else:
        guilds["guilds"].append({
            "id": str(guild.id),
            "prefix": "?",
            "tornapikey": "",
            "tornapikey2": ""
        })
        dbutils.write("guilds", guilds)
    if str(guild.id) not in vaults:
        vaults[guild.id] = {
            "channel": "",
            "role": "",
            "channel2": "",
            "role2": "",
            "banking": "",
            "banking2": ""
        }
        dbutils.write("vault", vaults)


@bot.event
async def on_message(message):
    if message.author.bot:
        return None
    if str(message.channel.id) == dbutils.read("vault")[str(message.guild.id)]["banking"] \
            and message.clean_content[0] != get_prefix(client, message):
        await message.delete()
        embed = discord.Embed()
        embed.title = "Bot Channel"
        embed.description = "This channel is only for vault withdrawals. Please do not post any other messages in" \
                            " this channel."
        message = await message.channel.send(embed=embed)
        await asyncio.sleep(30)
        await message.delete()

    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed()
        embed.title = "Cooldown"
        embed.description = f'You are on cooldown. Please try again in {round(error.retry_after, 2)} seconds.'
        message = await ctx.send(embed=embed)
        if str(ctx.message.channel.id) == dbutils.get_vault(ctx.guild.id, "banking"):
            await asyncio.sleep(30)
            await message.delete()
    else:
        print(error)
        raise error

@bot.event
async def on_member_join(member):
    data = dbutils.read('users')

    if str(member.id) in data:
        return None
    if member.bot:
        return None
    data[member.id] = {
        "tornid": "",
        "tornapikey": "",
        "generaluse": False
    }
    dbutils.write("users", data)

bot.run(dbutils.read("guilds")["bottoken"])
file.close()
