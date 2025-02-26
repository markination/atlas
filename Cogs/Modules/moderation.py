import discord
from discord.ext import commands
from discord import app_commands
from Utils.constants import emojis, ATLAS_GREEN
from Utils.utils import check_module_status, permission_check, get_guild_config
from Utils.embeds import MissingPermissions, ModuleDisabled, MissingConfigChannel, ChannelNotFound, ChannelSendFailure
import secrets
import string





class Moderation(commands.Cog):
    def __init__(self, client: commands.Bot):
        super().__init__()  
        self.client = client

    @commands.hybrid_command(name="warn", description="Warn a user")
    @app_commands.describe(user="The user you want to warn", reason="The reason for the warning", silent="Whether to DM the user or not")
    async def warn(self, ctx: commands.Context, user: discord.Member, reason: str, silent: bool = False):
        if ctx.interaction:
            try:
                await ctx.interaction.response.defer()
            except:
                pass

        if not await permission_check(ctx, "staff"):
            data = MissingPermissions()

            return await ctx.send(ephemeral=True,
                                  embed=data["embed"],
                                  view=data["view"],
                                  allowed_mentions=discord.AllowedMentions.none())

        status = await check_module_status(guild_id=ctx.guild.id,
                                           module="moderation_module",
                                           mongo=self.client.mongo)

        if status is False:
            data = ModuleDisabled()
            return await ctx.send(ephemeral=True,
                                  embed=data["embed"],
                                  view=data["view"],
                                  allowed_mentions=discord.AllowedMentions.none())

        config = await get_guild_config(ctx.guild.id, self.client.mongo)
        module_config = config["Config"]["moderation_module"]

        log_channel_id = module_config.get("log_channel_id")
        if not log_channel_id:
            data = MissingConfigChannel()

            return await ctx.send(ephemeral=True,
                                  embed=data["embed"],
                                  view=data["view"],
                                  allowed_mentions=discord.AllowedMentions.none())

        log_channel = ctx.guild.get_channel(log_channel_id)
        if not log_channel:
            data = ChannelNotFound()

            return await ctx.send(ephemeral=True,
                                  embed=data["embed"],
                                  view=data["view"],
                                  allowed_mentions=discord.AllowedMentions.none())

        timestamp = discord.utils.utcnow()

        if config.get("premium") is True:
            case_id = await self.client.mongo["Atlas"]["Warnings"].count_documents({"guild_id": ctx.guild.id}) + 1
        else:
            case_id = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
            while await self.client.mongo["Atlas"]["Warnings"].find_one({"case_id": case_id}):
                case_id = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))

        embed = discord.Embed(title=f"Case #{case_id}",
                              color=discord.Color.dark_embed(),
                              timestamp=timestamp,
                              description=
                              f"> **User:** {user.mention} ``({user.id})``\n"
                              f"> **Moderator:** {ctx.author.mention} ``({ctx.author.id})``\n"
                              f"> **Action:** Warning\n"
                              f"> **Reason:** {reason}\n")
        embed.set_footer(text=f"Case ID: {case_id}", icon_url=ctx.author.display_avatar.url)
        try:
            await log_channel.send(embed=embed,
                                   allowed_mentions=discord.AllowedMentions.none())
        except discord.HTTPException:
            data = ChannelSendFailure()

            return await ctx.send(ephemeral=True,
                                  embed=data["embed"],
                                  view=data["view"],
                                  allowed_mentions=discord.AllowedMentions.none())

        try:
            await self.client.mongo["Atlas"]["Moderation"].insert_one({
                "Case.guild_id": ctx.guild.id,
                "Case.case_id": case_id,
                "Case.action": "warn",
                "Case.reason": reason,
                "Case.timestamp": timestamp,
                "User.id": user.id,
                "User.name": user.name,
                "Moderator.id": ctx.author.id,
                "Moderator.name": ctx.author.name})

        except Exception as e:
            print(f"Error inserting warn into database: {e} ({ctx.guild.id}")
            return await ctx.send(content=f"{emojis['no']} **{ctx.author.name},** I couldn't warn the user.",
                                  ephemeral=True)

        await ctx.send(content=f"{emojis['yes']} **{ctx.author.name},** I have warned {user.name} for ``{reason}``.",
                       ephemeral=True)

        if not silent:
            try:
                await user.send(f"{emojis['moderation']} You have been warned in **{ctx.guild.name}** for ``{reason}``.")
            except discord.HTTPException:
                pass

        return












async def setup(client: commands.Bot) -> None:
    await client.add_cog(Moderation(client))