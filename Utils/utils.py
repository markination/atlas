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


async def permission_check(ctx: commands.Context, permission: str) -> bool:
    """
    Checks if the user has the required permission based on role IDs.

    Args:
        ctx: commands.Context - The context of the command.
        permission: str - The required permission level ("staff" or "manage").

    Returns:
        bool - True if the user has the required permission, False otherwise.
    """

    db = ctx.bot.mongo["Atlas"]["Config"]
    find = await db.find_one({"_id": ctx.guild.id})

    if not find:
        return False

    if permission == "staff":
        staff_roles = find.get("staff_roles", [])

        user_role_ids = {role.id for role in ctx.author.roles}

        return any(role_id in user_role_ids for role_id in staff_roles)

    if permission == "manage":
        staff_roles = find.get("management_roles", [])

        user_role_ids = {role.id for role in ctx.author.roles}

        return any(role_id in user_role_ids for role_id in staff_roles)

    return False



