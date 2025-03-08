import discord
from discord.ext import commands, tasks
from Utils.constants import emojis, ATLAS_GREEN
from Cogs.Config.menu import ConfigPanel
import tracemalloc
import objgraph
from collections import Counter



class Configuration(commands.Cog):
    def __init__(self, client: commands.Bot):
        super().__init__()  
        self.client = client

    @commands.hybrid_command(name="config", description="Configure the settings for this guild")
    async def config(self, ctx: commands.Context):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send(ephemeral=True, content=f"{emojis['no']} **{ctx.author.name},** you need **administrator** to use this.")
        embed = discord.Embed(title="", color=discord.Color.dark_embed(), description=f"**{emojis['settings']} Setting Up**\n> To setup Atlas, please choose an option from below.\n\n**{emojis['help']} Support**\n> If you have an issue with setting up or the bot in general, join our [support server](https://discord.gg/x2meHZN38N)")
        embed.set_thumbnail(url=(ctx.guild.icon.url if ctx.guild.icon else ctx.author.display_avatar.url))
        embed.set_author(icon_url=(ctx.guild.icon.url if ctx.guild.icon else ctx.author.display_avatar.url), name=ctx.guild.name)
        view = discord.ui.View(timeout=None)
        view.add_item(ConfigPanel(mongo=self.client.mongo))
        await ctx.send(
            embed=embed,
            view=view,
            ephemeral=True)

    @commands.hybrid_command(
        name="memory",
        description="Check memory usage and object growth")
    async def memory(
            self, ctx):
        """Check memory usage and object growth."""
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics(
            "lineno")

        leaks = objgraph.get_leaking_objects()

        _typestats = objgraph.typestats(
            shortnames=False)

        def sanity(
                left,
                name,
                *,
                _stats=_typestats):
            """Compare expected and actual object counts."""
            try:
                right = \
                _stats[
                    name]
            except KeyError:
                return f"{name}: {left}. Not found"
            else:
                cmp = '!=' if left != right else '=='
                return f"{name}: {left} {cmp} {right}"

        channels = Counter(
            type(
                c)
            for
            c
            in
            self.client.get_all_channels())

        sanity_results = [
            sanity(
                channels[
                    discord.TextChannel],
                'discord.channel.TextChannel'),
            sanity(
                channels[
                    discord.VoiceChannel],
                'discord.channel.VoiceChannel'),
            sanity(
                128,
                'discord.channel.DMChannel'),
            sanity(
                channels[
                    discord.CategoryChannel],
                'discord.channel.CategoryChannel'),
            sanity(
                len(self.client.guilds),
                'discord.guild.Guild'),
            sanity(
                5000,
                'discord.message.Message'),
            sanity(
                len(self.client.users),
                'discord.user.User'),
            sanity(
                sum(
                    1
                    for
                    _
                    in
                    self.client.get_all_members()),
                'discord.member.Member'),
            sanity(
                len(self.client.emojis),
                'discord.emoji.Emoji'),
        ]

        embed = discord.Embed(
            title="Memory Usage & Leaks",
            color=discord.Color.red())
        embed.add_field(
            name="Leaking Objects",
            value=f"{len(leaks)} objects detected",
            inline=False)

        top_memory = "\n".join(
            [
                f"**#{i + 1}**: `{stat.traceback[0].filename}:{stat.traceback[0].lineno}` - `{stat.size / 1024:.1f} KiB`"
                for
                i, stat
                in
                enumerate(
                    top_stats[
                    :5])]
        )
        embed.add_field(
            name="Top Memory Allocations",
            value=top_memory or "No data",
            inline=False)

        embed.add_field(
            name="Cache Sanity",
            value="\n".join(
                sanity_results) or "No issues",
            inline=False)

        await ctx.send(
            embed=embed)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Configuration(client))