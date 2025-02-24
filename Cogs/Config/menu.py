import discord 
from discord.ext import commands 
from Utils.constants import emojis
from Cogs.Config.Modules import permissions, moderation


class ModulesView(discord.ui.Select):
    def __init__(self, modules, mongo):
        self.mongo = mongo

        options = [
            discord.SelectOption(
                label="Moderation",  
                value="moderation_module",
                default=modules.get("moderation_module", {}).get("is_enabled", False)
            ),
            discord.SelectOption(
                label="test",
                value="test2",
                default=modules.get(
                    "test2",
                    {}).get(
                    "is_enabled",
                    False)
            ),
        ]

        super().__init__(placeholder="Choose Enabled Modules", max_values=len(options), min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild_id = interaction.guild.id
        config_collection = self.mongo["Atlas"]["Config"]
        
        guild_config = await config_collection.find_one({"_id": guild_id})
        
        if not guild_config or "Config" not in guild_config:
            return await interaction.followup.send(f"{emojis['no']} **{interaction.user.name},** no guild configuration was found.", ephemeral=True)
            
        
        updated_config = guild_config["Config"]
        
        for module_name, module_data in updated_config.items():
            module_data["is_enabled"] = module_name in self.values
        
        await config_collection.update_one({"_id": guild_id}, {"$set": {"Config": updated_config}})
        
        return await interaction.followup.send(f"{emojis['yes']} **{interaction.user.name},** I have updated the modules.", ephemeral=True)



        

class ConfigPanel(discord.ui.Select):
    def __init__(self, mongo):
        self.mongo = mongo
        options=[
            discord.SelectOption(label="Modules", description="Manage your servers enabled module.",value="modules" ,emoji=emojis["modules"]),
            discord.SelectOption(label="Permissions", description="Manage what roles can do what", value="perms", emoji=emojis["permissions"]),
            discord.SelectOption(label="Moderation", description="Manage your servers moderation", value="moderation", emoji=emojis["moderation"])

            ]
        super().__init__(placeholder="Configuration Menu",max_values=1,min_values=1,options=options, row=4)
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()


        if self.values[0] == "perms":
            db = self.mongo["Atlas"]["Config"]
            
            find = await db.find_one({"_id": interaction.guild.id})
            
            modules = find["Config"] if find and "Config" in find else {}
            staff_roles_find = find.get("staff_roles", [])
            mgmt_roles_find = find.get("management_roles", [])

            all_roles = {role.id: role for role in interaction.guild.roles}
            all_role_ids = set(staff_roles_find + mgmt_roles_find)

            staff_roles = [all_roles.get(role_id) for role_id in staff_roles_find if
                           role_id in all_role_ids and role_id in all_roles]
            mgmt_roles = [all_roles.get(role_id) for role_id in mgmt_roles_find if
                          role_id in all_role_ids and role_id in all_roles]

            staff_roles = [role for role in staff_roles if role is not None]
            mgmt_roles = [role for role in mgmt_roles if role is not None]

            view = permissions.PermissionsView(
                mongo=self.mongo, 
                staff_roles=staff_roles,
                mgmt_roles=mgmt_roles 
            )

            embed = discord.Embed(
                title="", 
                description="> In this view, you can select which roles have higher permissions than normal members.", 
                color=discord.Color.dark_embed()
            )
            embed.set_thumbnail(url=(interaction.guild.icon.url if interaction.guild.icon else interaction.user.display_avatar.url))
            embed.set_author(
                icon_url=(interaction.guild.icon.url if interaction.guild.icon else interaction.user.display_avatar.url),
                name=interaction.guild.name
            )

            return await interaction.edit_original_response(embed=embed, view=view)
        
        if self.values[0] == "modules":
            db = self.mongo["Atlas"]["Config"]
            find = await db.find_one({"_id": interaction.guild.id})
            modules = find["Config"] if find and "Config" in find else {}

            view = discord.ui.View(timeout=None)
            view.add_item(ModulesView(mongo=self.mongo, modules=modules))
            view.add_item(ConfigPanel(mongo=self.mongo))

            embed = discord.Embed(
                title="", 
                description="> In this view, you can Enable and Disable different modules and their functionality.", 
                color=discord.Color.dark_embed()
            )
            embed.set_thumbnail(url=(interaction.guild.icon.url if interaction.guild.icon else interaction.user.display_avatar.url))
            embed.set_author(
                icon_url=(interaction.guild.icon.url if interaction.guild.icon else interaction.user.display_avatar.url),
                name=interaction.guild.name
            )

            return await interaction.edit_original_response(view=view, embed=embed)

        if self.values[0] == "moderation":
            db = self.mongo["Atlas"]["Config"]

            find = await db.find_one({"_id": interaction.guild.id})

            modules = find["Config"] if find and "Config" in find else {}
            modlog_channel = modules.get("moderation_module", {}).get("log_channel_id")
            channel = interaction.guild.get_channel(modlog_channel)

            view = moderation.ModerationView(
                mongo=self.mongo,
                modlog_channel=channel
            )

            embed = discord.Embed(
                title="",
                description="> In this view, you can config the moderation settings.",
                color=discord.Color.dark_embed()
            )
            embed.set_thumbnail(url=(
                interaction.guild.icon.url if interaction.guild.icon else interaction.user.display_avatar.url))
            embed.set_author(
                icon_url=(
                    interaction.guild.icon.url if interaction.guild.icon else interaction.user.display_avatar.url),
                name=interaction.guild.name
            )

            return await interaction.edit_original_response(view=view, embed=embed)
