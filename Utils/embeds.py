import discord


def ModuleNotFound():
    embed = discord.Embed(
        title="Module Not Found",
        description=f"The module was not found.",
        color=discord.Color.brand_red(),
        timestamp=discord.utils.utcnow()
    ).add_field(
        name="Trouble Shooting",
        value=f"> **1.** Run ``/config``\n **2.** Find the module in the dropdown\n **3.** Configure the module\n **4.** On the dropdown, go to Modules\n**5.** In the Enabled dropdown, find the Module and make sure it is selected.",
        inline=True
    )

    view = discord.ui.View(timeout=None)
    view.add_item(item=discord.ui.Button(style=discord.ButtonStyle.url, label="Support", url="https://discord.gg/mmVYkZRG8h"))
    view.add_item(item=discord.ui.Button(style=discord.ButtonStyle.url, label="Docs", url="https://docs.atlasmgmt.xyz"))
    return {"embed": embed, "view": view}

def MissingPermissions():
    embed = discord.Embed(
        title="Missing Permissions",
        description=f"You are missing the required permissions to run this command.",
        color=discord.Color.brand_red(),
        timestamp=discord.utils.utcnow())

    view = discord.ui.View(timeout=None)
    view.add_item(item=discord.ui.Button(style=discord.ButtonStyle.url, label="Support", url="https://discord.gg/mmVYkZRG8h"))
    view.add_item(item=discord.ui.Button(style=discord.ButtonStyle.url, label="Docs", url="https://docs.atlasmgmt.xyz"))
    return {"embed": embed, "view": view}
