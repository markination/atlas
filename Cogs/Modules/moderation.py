import discord
from discord.ext import commands, tasks
from discord import app_commands
from Utils.constants import emojis, ATLAS_GREEN
from Utils.utils import check_module_status
from Cogs.Config.menu import ConfigPanel




class hfhfhfh(commands.Cog):
    def __init__(self, client: commands.Bot):
        super().__init__()  
        self.client = client

   

async def setup(client: commands.Bot) -> None:
    await client.add_cog(hfhfhfh(client))