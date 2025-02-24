import discord
from Utils.constants import emojis

class ModlogChannel(discord.ui.ChannelSelect):
    def __init__(self, mongo, modlog_channel):
        self.mongo = mongo
        super().__init__(placeholder="Select a mod log channel", max_values=1, min_values=1, row=1, default_values=[modlog_channel])

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        guild_id = interaction.guild.id
        db = self.mongo["Atlas"]["Config"]
        print("hi!!")

        insert = await db.update_one(
            {"_id": guild_id},
            {"$set": {"Config.moderation_module.log_channel_id": self.values[0].id}},
            upsert=True
        )
        return await interaction.followup.send(ephemeral=True, content=f"{emojis['yes']} **{interaction.user.name},** I have saved the moderation channel.")

class ModerationView(discord.ui.View):
    def __init__(self, mongo, modlog_channel):
        super().__init__(timeout=None)
        self.mongo = mongo


        self.add_item(item=ModlogChannel(mongo=self.mongo, modlog_channel=modlog_channel))

        from Cogs.Config.menu import ConfigPanel
        self.add_item(ConfigPanel(mongo=mongo))



