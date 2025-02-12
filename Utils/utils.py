
async def check_module_status(guild_id, module, mongo):
    """
    Parameters:
        guild_id: Integer = The ID of the guild that the module is under
        Module: String = The name of the module in the Config dict that you are looking for
        Mongo: AsyncioMotorClient = The mongo connection

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
            return False # shouldnt this raise a keyerror exception anyways?? idk might make the check redundant but oh well
        
        enabled = config["is_enabled"]
        return enabled
        


    except Exception:
        return False
    
