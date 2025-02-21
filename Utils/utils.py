import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient


async def check_module_status(guild_id, module, mongo):
    """
    Args:
        guild_id: Integer = The ID of the guild that the module is under
        module: String = The name of the module in the Config dict that you are looking for
        mongo: AsyncioMotorClient = The mongo connection

    Returns:
        Boolean
    """

    try:
        db = mongo["Atlas"]["Config"]
        find = await db.find_one({"_id": guild_id})

        if not find:
            return False
        
        config = find["Config"][module]
        if not config:
            return False
        
        enabled = config["is_enabled"]
        return enabled
        


    except Exception:
        return False

async def permission_check(ctx: commands.Context, permission: str):
    """
    Args:
        ctx: commands.Context = Context of the command
        permission: str = "staff" / "manage"
        database: AsyncIOMotorClient = The mongo connection

    Returns:
        boolean

    """

    if permission == "staff":
