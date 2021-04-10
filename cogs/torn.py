import os, sys, discord
from aiohttp import ClientSession, web
from discord.ext import commands

if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and try again.")
else:
    import config

class Torn(commands.Cog, name="torn"):
    def __init__(self, bot):
        self.bot = bot
        self.key = "TORN API"

    async def get(self, url):
      async with ClientSession() as session:
        async with session.get(url) as response:
          if response.status != 200:
            raise Exception("Torn API is down.")

          if "Error" in await response.json():
            error = await response.json()['error']
            raise Exception(error)
          
          return await response.json()

    @commands.command(name="profile")
    async def profile(self, ctx, id=None):
      """
      Returns the profile of the user
      """

    # if type(id) is not int or id < 1:
    #   embed = discord.Embed()
    #   embed.title = "Error"
    #   embed.description = "The inputted ID must be an integer whose value is greater than one."
    #   await ctx.send(embed=embed)
    #   return None

      if id is None:
        data = await self.get(f'https://api.torn.com/user/?selections=basic&key={self.key}')
        faction_data = await self.get(f'https://api.torn.com/faction/?selections=basic&key={self.key}')
      else:
        data = await self.get(f'https://api.torn.com/user/{id}?selections=basic,profile&key={self.key}')
        faction_data = await self.get(f'https://api.torn.com/faction/{data.get("faction").get("faction_id")}?selections=basic&key={self.key}')
    
      embed = discord.Embed()
      embed.title = "User Profile"
      embed.add_field(name="Name", value=data.get('name'), inline=False)
      embed.add_field(name="Level", value=data.get('level'), inline=False)
      embed.add_field(name="Gender", value=data.get('gender'), inline=False)
      embed.add_field(name="Faction Name", value=faction_data.get('name'), inline=False)

      await ctx.send(embed=embed)

    @commands.command(name="faction")
    async def faction(self, ctx, id=None):
      """
      Returns the Faction profile of the user
      """

    # if type(id) is not int or id < 1:
    #   embed = discord.Embed()
    #   embed.title = "Error"
    #   embed.description = "The inputted ID must be an integer whose value is greater than one."
    #   await ctx.send(embed=embed)
    #   return None

      if id is None:
        faction_data = await self.get(f'https://api.torn.com/faction/?selections=basic&key={self.key}')
      else:
        faction_data = await self.get(f'https://api.torn.com/faction/{id}?selections=basic&key={self.key}')
    
      embed = discord.Embed()
      embed.title = "Faction"
      embed.add_field(name="Name", value=faction_data.get('name'), inline=False)
      embed.add_field(name="Tag", value=faction_data.get('tag'), inline=False)
      embed.add_field(name="Age", value=faction_data.get('age'), inline=False)
      embed.add_field(name="Total Respect", value=faction_data.get('respect'), inline=False)

      await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def addid(self, ctx, id:int):
        '''
        Adds the user's Torn ID to the database (across servers).
        '''
        
        if dbutils.get_user(ctx.message.author.id)["tornid"] != "":
          embed = discord.Embed()
        embed.title = "ID Already Set"
        embed.description = "Your ID is already set in the database."
        await ctx.send(embed=embed)
        return None
            
        request = await tornget(ctx, f'https://api.torn.com/user/{id}?  selections=discord&key=')
              
        if request["discord"]["discordID"] == "":
          embed = discord.Embed()
        embed.title = "ID Not Set"
        embed.description = "Your Discord ID is not set in the Torn database. To set your Discord ID in the Torn" \
                                "database, visit the official Torn Discord server and verify yourself."
        await ctx.send(embed=embed)

        log(f'{ctx.message.author.name} has attempted to set id, but is not verified in the official Discord '
                f'server.', self.log_file)
        return None

        if request["discord"]["discordID"] != str(ctx.message.author.id):
          embed = discord.Embed()
          embed.title = "Invalid ID"
          embed.description = f'Your Discord ID is not the same as the Discord ID stored in Torn\'s' \
                                f' database for your given Torn ID.'
        await ctx.send(embed=embed)
        log(f'{ctx.message.author.name} has attempted to set their Torn ID to be {id}, but their Discord ID '
            f'({ctx.message.author.id} does not match the value in Torn\'s DB.', self.log_file)
        return None

        data = dbutils.read("users")
        data[str(ctx.message.author.id)]["tornid"] = str(id)
        dbutils.write("users", data)

        embed = discord.Embed()
        embed.title = "ID Set"
        embed.description = "Your ID has been set in the database."
        await ctx.send(embed=embed)
        log(f'{ctx.message.author.name} has set their id which is {id}.', self.log_file)
        
        
    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def addkey(self, ctx, key):
      '''
      Adds the user's Torn API key to the database (across servers). The Torn API key can be enabled and disabled for
      random, global use by the bot by running the `?enkey` and `?diskey` respectively. By default, user's Torn API
      key will not be used randomly and globally.
      '''

      if type(ctx.message.channel) != discord.DMChannel:
          await ctx.message.delete()

      request = await tornget(ctx, f'https://api.torn.com/user/?selections=&key=', key=key)

      if dbutils.get_user(ctx.message.author.id, "tornid") == "":
          data = dbutils.read("users")
          data[str(ctx.message.author.id)]["tornid"] = request["player_id"]
          dbutils.write("users", data)

      data = dbutils.read("users")
      data[str(ctx.message.author.id)]["tornapikey"] = key
      dbutils.write("users", data)

      embed = discord.Embed()
      embed.title = "API Key Set"
      embed.description = f'{ctx.message.author.name} has set their API key.'
      await ctx.send(embed=embed)
      log(f'{ctx.message.author.name} has set their Torn API key.', self.log_file)

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def rmkey(self, ctx):
        '''
        Removes the user's Torn API key from the database.
        '''

        if dbutils.get_user(ctx.message.author.id, "tornapikey") == "":
            embed = discord.Embed()
            embed.title = "API Key"
            embed.description = f'The API key of {ctx.message.author.name} has not been set yet, and therefore can ' \
                                f'not be removed,'
            await ctx.send(embed=embed)

        data = dbutils.read("users")
        data[str(ctx.message.author.id)]["tornapikey"] = ""
        data[str(ctx.message.author.id)]["generaluse"] = False
        dbutils.write("users", data)

        embed = discord.Embed()
        embed.title = "API Key"
        embed.description = f'The API key of {ctx.message.author.name} has been removed from the database.'
        await ctx.send(embed=embed)
        log(f'{ctx.message.author.name} has removed their Torn API key.', self.log_file)

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def enkey(self, ctx):
        '''
        Enables the user's Torn API key for random, global use by the bot. Can be disabled by running `?diskey`.
        '''

        if dbutils.get_user(ctx.message.author.id, "generaluse"):
            embed = discord.Embed()
            embed.title = "API Key"
            embed.description = f'The API key of {ctx.message.author.name} is already authorized for general use.'
            await ctx.send(embed=embed)
            return None

        if dbutils.get_user(ctx.message.author.id, "tornapikey") == "":
            embed = discord.Embed()
            embed.title = "API Key"
            embed.description = f'No API key is currently set for {ctx.message.author.name}.'
            await ctx.send(embed=embed)
            return None

        data = dbutils.read("users")
        data[str(ctx.message.author.id)]["generaluse"] = True
        dbutils.write("users", data)

        embed = discord.Embed()
        embed.title = "API Key"
        embed.description = f'The API key of {ctx.message.author.name} has been enabled for random, global use by ' \
                            f'the bot. The API key can be removed from random, global use by running `?diskey`.'
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def diskey(self, ctx):
        '''
        Disables the user's Torn API key for random, global use by the bot. Can be enabled by running `?enkey`.
        '''

        if not dbutils.get_user(ctx.message.author.id, "generaluse"):
            embed = discord.Embed()
            embed.title = "API Key"
            embed.description = f'The API key of {ctx.message.author.name} is already not authorized for general use.'
            await ctx.send(embed=embed)
            return None

        if dbutils.get_user(ctx.message.author.id, "tornapikey") == "":
            embed = discord.Embed()
            embed.title = "API Key"
            embed.description = f'No API key is currently set for {ctx.message.author.name}.'
            await ctx.send(embed=embed)
            return None

        data = dbutils.read("users")
        data[str(ctx.message.author.id)]["generaluse"] = False
        dbutils.write("users", data)

        embed = discord.Embed()
        embed.title = "API Key"
        embed.description = f'The API key of {ctx.message.author.name} has been disabled for random, global use by ' \
                            f'the bot. The API key can be added to random, global use by running `?enkey`.'
        await ctx.send(embed=embed)

  
def setup(bot):
    bot.add_cog(Torn(bot))
