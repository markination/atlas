import discord 
from discord.ext import commands 
from Utils.constants import emojis

class ModulesView(discord.ui.Select):
    def __init__(self, context, message, mongo):
        self.context = context
        self.mongo = mongo

        options=[
            discord.SelectOption(label="Suggestions", value="suggestion_module"),
            discord.SelectOption(label="Suggestions2", value="sugges2tion_module")


            ]
        super().__init__(placeholder="Select an option", max_values=len(options), min_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)         





        

class ConfigPanel(discord.ui.Select):
    def __init__(self, context, message, mongo):
        self.mongo = mongo
        self.context = context
        self.message = message
        options=[
            #discord.SelectOption(label="Permissions", description="Configure the permissions module.", value="perms", emoji=emojis.permissions_emoji),
            discord.SelectOption(label="Modules", description="Manage your servers enabled modules.",value="modules" ,emoji=emojis["modules"])

            ]
        super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options)
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.values[0] == "modules":
            view = discord.ui.View(timeout=None)
            view.add_item(ModulesView(mongo=self.mongo, context=self.context, message=self.message))
            view.add_item(ConfigPanel(mongo=self.mongo, context=self.context, message=self.message))
            embed = discord.Embed(title="", description=f"> In this view, you can Enable and Disable different modules and their functionality.", color=discord.Color.dark_embed())
            embed.set_thumbnail(url=(self.context.guild.icon.url if self.context.guild.icon else self.context.author.display_avatar.url))
            embed.set_author(icon_url=(self.context.guild.icon.url if self.context.guild.icon else self.context.author.display_avatar.url), name=self.context.guild.name)
            return await self.message.edit(view=view, embed=embed)

