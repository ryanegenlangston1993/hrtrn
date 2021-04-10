import discord
from discord.ext import commands
from required import *
import dbutils


class Superuser(commands.Cog):
    def __init__(self, client):
        self.client = client
        
        

    def is_superuser(self, id):
        return True if dbutils.get_superuser() == id else False

def setup(bot):
  bot.add_cog(Superuser(bot))
