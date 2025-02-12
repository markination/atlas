import sys
sys.dont_write_bytecode = True
import os
import dotenv
import discord
from discord.ext import commands
from cogwatch import watch
from motor.motor_asyncio import AsyncIOMotorClient

dotenv.load_dotenv()

TOKEN = os.getenv(os.getenv("ENV"))

intents = discord.Intents.all()


class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix='!!', intents=intents)
        self.mongo = None  

    @watch(path='Cogs', preload=True)
    async def on_ready(self):
        self.mongo = AsyncIOMotorClient(os.getenv("MONGO"))

        print(f"Commands Synced Globally: {len(self.tree.get_commands())}")
        print('Bot is ready.')
        await self.change_presence(activity=discord.CustomActivity("Atlas"))

        await self.tree.sync()

    async def close(self):
        if self.mongo:
            self.mongo.close()  
        await super().close()

discordbot = Bot()

if __name__ == '__main__':
    discordbot.run(TOKEN, reconnect=True)