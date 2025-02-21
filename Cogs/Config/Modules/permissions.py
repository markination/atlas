import discord
from Utils.constants import emojis
import pymongo
import os

class StaffTeamRole(discord.ui.RoleSelect):
    def __init__(self, mongo, ctx, staff_roles):
        self.ctx = ctx
        self.mongo = mongo
        super().__init__(placeholder="Select your staff roles", max_values=3, min_values=1, row=1, default_values=staff_roles)

    async def callback(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            embed = discord.Embed(description="This is not your panel!", color=discord.Color.dark_embed())
            embed.set_author(icon_url=interaction.user.display_avatar.url, name=interaction.user.name)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.response.defer()

        role_ids = [role.id for role in self.values]
        guild_id = interaction.guild.id
        db = self.mongo["Atlas"]["Config"]

        await db.update_one(
            {"_id": guild_id},
            {"$set": {"staff_roles": role_ids}},
            upsert=True
        )
        return await interaction.followup.send(ephemeral=True, content=f"{emojis['yes']} **{interaction.user.name},** I have saved the staff roles")


class ManagementRole(discord.ui.RoleSelect):
    def __init__(self, mongo, ctx, management_roles):
        self.ctx = ctx
        self.mongo = mongo

        super().__init__(placeholder="Select your management roles", max_values=3, min_values=1, row=2, default_values=management_roles)

    async def callback(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            embed = discord.Embed(description="This is not your panel!", color=discord.Color.dark_embed())
            embed.set_author(icon_url=interaction.user.display_avatar.url, name=interaction.user.name)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.response.defer(ephemeral=True)

        role_ids = [role.id for role in self.values]
        guild_id = interaction.guild.id
        db = self.mongo["Atlas"]["Config"]

        await db.update_one(
            {"_id": guild_id},
            {"$set": {"management_roles": role_ids}},
            upsert=True
        )
        return await interaction.followup.send(ephemeral=True, content=f"{emojis['yes']} **{interaction.user.name},** I have saved the management roles")

class PermissionsView(discord.ui.View):
    def __init__(self, ctx, mongo, message, staff_roles, mgmt_roles):
        super().__init__(timeout=None)
        self.message = message
        self.ctx = ctx
        self.mongo = mongo

        self.staff_role_view = StaffTeamRole(ctx=self.ctx, mongo=mongo, staff_roles=staff_roles)
        self.management_role_view = ManagementRole(ctx=self.ctx, mongo=mongo, management_roles=mgmt_roles)

        self.add_item(item=self.staff_role_view)
        self.add_item(item=self.management_role_view)

        from Cogs.Config.menu import ConfigPanel
        self.add_item(ConfigPanel(message=self.message, context=self.ctx, mongo=mongo))



