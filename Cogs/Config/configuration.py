import discord
from discord.ext import commands, tasks
from discord import app_commands
from Utils.constants import emojis, ATLAS_GREEN
from Cogs.Config.menu import ConfigPanel




class Configuration(commands.Cog):
    def __init__(self, client: commands.Bot):
        super().__init__()  
        self.client = client

    @commands.hybrid_command(name="config", description="Configure the settings for this guild")
    async def config(self, ctx: commands.Context):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send(ephemeral=True, content=f"{emojis['no']} **{ctx.author.name},** you need **administrator** to use this.")
        embed = discord.Embed(title="", color=discord.Color.dark_embed(), description=f"{emojis['settings']} Select an Option below to manage your server")
        embed.set_thumbnail(url=(ctx.guild.icon.url if ctx.guild.icon else ctx.author.display_avatar.url))
        embed.set_author(icon_url=(ctx.guild.icon.url if ctx.guild.icon else ctx.author.display_avatar.url), name=ctx.guild.name)
        view = discord.ui.View(timeout=None)
        
        msg = await ctx.send(embed=embed, view=view)
        view.add_item(ConfigPanel(context=ctx, mongo=self.client.mongo, message=msg))
        await msg.edit(view=view)

    @app_commands.command(name="penis", description="Configure the settings for this guild")
    async def penis(self, i: discord.Interaction):
        return


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Configuration(client))