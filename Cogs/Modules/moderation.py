import discord
from discord.ext import commands
from discord import app_commands
from Utils.constants import emojis, ATLAS_GREEN
from Utils.utils import check_module_status, permission_check
from Utils.embeds import ModuleNotFound, MissingPermissions
from Cogs.Config.menu import ConfigPanel




class Moderation(commands.Cog):
    def __init__(self, client: commands.Bot):
        super().__init__()  
        self.client = client

    @commands.hybrid_command(name="warn", description="Warn a user")
    @app_commands.describe(user="The user you want to warn", reason="The reason for the warning", silent="Whether to DM the user or not")
    async def warn(self, ctx: commands.Context, user: discord.Member, reason: str, silent: bool = False):
        if not await permission_check(ctx, "staff"):
            data = MissingPermissions()

            return await ctx.send(ephemeral=True,
                                  embed=data["embed"],
                                  view=data["view"],
                                  allowed_mentions=discord.AllowedMentions.none())

        status = await check_module_status(guild_id=ctx.guild.id,
                                           module="moderation_module",
                                           mongo=self.client.mongo)

        if isinstance(status, bool):
            data = ModuleNotFound()

            return await ctx.send(ephemeral=True,
                                  embed=data["embed"],
                                  view=data["view"],
                                  allowed_mentions=discord.AllowedMentions.none())






   

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Moderation(client))