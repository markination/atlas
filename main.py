import sys
import os
import gc
gc.set_threshold(700, 10, 5)
import dotenv
import discord
import tracemalloc
import objgraph
from collections import Counter
from discord.ext import commands
from cogwatch import watch
from motor.motor_asyncio import AsyncIOMotorClient

sys.dont_write_bytecode = True

dotenv.load_dotenv()
TOKEN = os.getenv(os.getenv("ENV"))
MONGO_URI = os.getenv("MONGO")

intents = discord.Intents.default()
intents.members = True
intents.presences = False
intents.reactions = False
intents.typing = False
intents.voice_states = False

member_cache = discord.MemberCacheFlags.from_intents(intents)

tracemalloc.start()


class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix="!!", intents=intents, member_cache_flags=member_cache)
        self.mongo = None

    @watch(path="Cogs", preload=True)
    async def on_ready(self):
        if not self.mongo:
            self.mongo = AsyncIOMotorClient(os.getenv("MONGO"), maxPoolSize=10, minPoolSize=1)
        self._connection._dm_channel_cache = {}
        print(f"Commands Synced Globally: {len(self.tree.get_commands())}")
        print(f"Bot is ready, logged in as {self.user.name} ({self.user.id})")
        await self.change_presence(activity=discord.CustomActivity("Atlas Testr"))

        if not self.tree.get_commands():
            await self.tree.sync()

    async def close(self):
        if self.mongo:
            self.mongo.close()
        await super().close()


bot = Bot()


@commands.hybrid_command(name="memory", description="Check memory usage and object growth")
async def memory(ctx):
    """Check memory usage and object growth."""
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics("lineno")

    # Get memory leaks
    leaks = objgraph.get_leaking_objects()

    # Type statistics
    _typestats = objgraph.typestats(shortnames=False)

    def sanity(left, name, *, _stats=_typestats):
        """Compare expected and actual object counts."""
        try:
            right = _stats[name]
        except KeyError:
            return f"{name}: {left}. Not found"
        else:
            cmp = '!=' if left != right else '=='
            return f"{name}: {left} {cmp} {right}"

    # Cache sanity checks
    channels = Counter(type(c) for c in bot.get_all_channels())

    sanity_results = [
        sanity(channels[discord.TextChannel], 'discord.channel.TextChannel'),
        sanity(channels[discord.VoiceChannel], 'discord.channel.VoiceChannel'),
        sanity(128, 'discord.channel.DMChannel'),
        sanity(channels[discord.CategoryChannel], 'discord.channel.CategoryChannel'),
        sanity(len(bot.guilds), 'discord.guild.Guild'),
        sanity(5000, 'discord.message.Message'),
        sanity(len(bot.users), 'discord.user.User'),
        sanity(sum(1 for _ in bot.get_all_members()), 'discord.member.Member'),
        sanity(len(bot.emojis), 'discord.emoji.Emoji'),
    ]

    # Embed for readability
    embed = discord.Embed(title="Memory Usage & Leaks", color=discord.Color.red())
    embed.add_field(name="Leaking Objects", value=f"{len(leaks)} objects detected", inline=False)

    # Show top memory allocations
    top_memory = "\n".join(
        [f"**#{i+1}**: `{stat.traceback[0].filename}:{stat.traceback[0].lineno}` - `{stat.size / 1024:.1f} KiB`"
         for i, stat in enumerate(top_stats[:5])]
    )
    embed.add_field(name="Top Memory Allocations", value=top_memory or "No data", inline=False)

    # Sanity check results
    embed.add_field(name="Cache Sanity", value="\n".join(sanity_results) or "No issues", inline=False)

    await ctx.send(embed=embed)


if __name__ == "__main__":
    bot.run(TOKEN, reconnect=True)
