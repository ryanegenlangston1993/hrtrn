import os, sys, discord
import re

from urllib import parse, request
from discord.ext import commands
from discord.ext.commands import Cog, command

# Only if you want to use variables that are in the config.py file.
if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and try again.")
else:
    import config

# Here we name the cog and create a new class for the cog.
class Youtube(commands.Cog, name="Youtube"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="yt")
    async def yt(self, ctx, *, search): #get args and search videos on youtube
      global searchResults
      queryString= parse.urlencode({'search_query': search})
      htmlContent= request.urlopen('http://www.youtube.com/results?'+ queryString)
      searchResults=re.findall( r"watch\?v=(\S{11})", htmlContent.read().decode())#get videos id

      await ctx.send(f"We have found {len(searchResults)} results.\n\n Result:\nhttp://www.youtube.com/watch?v={searchResults[0]}") #get and send the first video

    """@command(name="nextyt")
        async def nextyt(ctx, option:int):
        leng = len(searchResults)
        if leng != 0:
        await ctx.send(f"http://www.youtube.com/watch?v={searchResults[option]}")
        else:
        await ctx.send("You haven't searched for any videos!!")"""

def setup(bot):
  bot.add_cog(Youtube(bot))


""""
 class Youtube(Cog):
	def __init__(self, bot):
		self.bot = bot


    @command(name="yt")
    async def yt
 
 command(name="yt")
    async def yt(ctx, *, search): #get args and search videos on youtube
      global searchResults
      queryString= parse.urlencode({'search_query': search}) #take the args from the user and parse that to a url
      htmlContent= request.urlopen('http://www.youtube.com/results?'+ queryString)
      searchResults=re.findall( r"watch\?v=(\S{11})", htmlContent.read().decode())#get videos id
      
      await ctx.send(f"Se han encontrado {len(searchResults)} resultados.\n\nPrimer Resultado:\nhttp://www.youtube.com/watch?v={searchResults[0]}") #get and send the first video

    @command(name="nextyt")
    async def nextyt(ctx, option:int):
      leng = len(searchResults)
      if leng != 0:
          await ctx.send(f"http://www.youtube.com/watch?v={searchResults[option]}")
      else:
          await ctx.send("No has buscado videos!! para ver los comandos utiliza: -help
 
def setup(bot):
    bot.add_cog(Template(bot))"""
