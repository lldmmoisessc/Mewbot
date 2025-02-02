# Buttons.py holds all the buttons necessary for use in Mobot
import nextcord


# The class queueButton is used for the queue command to move through the pages
# This is specifically the buttons are both enabled
class queueButton(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @nextcord.ui.button(label='Back', style=nextcord.ButtonStyle.red)
    async def back(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = False
        await interaction.response.edit_message(view=self)
        self.stop()

    @nextcord.ui.button(label='Next', style=nextcord.ButtonStyle.green)
    async def next(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = True
        await interaction.response.edit_message(view=self)
        self.stop()


# The class queueButton is used for the queue command to move through the pages
# This is specifically for when the Back Button is supposed to be disabled
class queueButtonBackDisabled(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @nextcord.ui.button(label='Back', style=nextcord.ButtonStyle.red, disabled=True)
    async def back(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = False
        await interaction.response.edit_message(view=self)
        self.stop()

    @nextcord.ui.button(label='Next', style=nextcord.ButtonStyle.green)
    async def next(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = True
        await interaction.response.edit_message(view=self)
        self.stop()


# The class queueButton is used for the queue command to move through the pages
# This is specifically for when the Next Button is supposed to be disabled
class queueButtonFrontDisabled(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @nextcord.ui.button(label='Back', style=nextcord.ButtonStyle.red)
    async def back(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = False
        await interaction.response.edit_message(view=self)
        self.stop()

    @nextcord.ui.button(label='Next', style=nextcord.ButtonStyle.green, disabled=True)
    async def next(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = True
        await interaction.response.edit_message(view=self)
        self.stop()


# THe class searchButton holds all the buttons used to make a selection in a search. The buttons correspond to the
# 1-5 buttons needed for a search
class songSearchButton(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=20)
        self.value = None

    @nextcord.ui.button(label='1', style=nextcord.ButtonStyle.blurple)
    async def one(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = 1
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()

    @nextcord.ui.button(label='2', style=nextcord.ButtonStyle.blurple)
    async def two(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = 2
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()

    @nextcord.ui.button(label='3', style=nextcord.ButtonStyle.blurple)
    async def three(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = 3
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()

    @nextcord.ui.button(label='4', style=nextcord.ButtonStyle.blurple)
    async def four(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = 4
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()

    @nextcord.ui.button(label='5', style=nextcord.ButtonStyle.blurple)
    async def five(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = 5
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()

    @nextcord.ui.button(label='Playlist', style=nextcord.ButtonStyle.red)
    async def playlist(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = -1
        self.stop()


class plistSearchButton(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=20)
        self.value = None

    @nextcord.ui.button(label='1', style=nextcord.ButtonStyle.blurple)
    async def one(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = 6
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()

    @nextcord.ui.button(label='2', style=nextcord.ButtonStyle.blurple)
    async def two(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = 7
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()

    @nextcord.ui.button(label='3', style=nextcord.ButtonStyle.blurple)
    async def three(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = 8
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()

    @nextcord.ui.button(label='4', style=nextcord.ButtonStyle.blurple)
    async def four(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = 9
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()

    @nextcord.ui.button(label='5', style=nextcord.ButtonStyle.blurple)
    async def five(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = 10
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()

    @nextcord.ui.button(label='Song', style=nextcord.ButtonStyle.green)
    async def song(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = 0
        self.stop()


# This class is for buttons to prompt a user to select a playlist or song when a conflict is detected
class playlistSelectButton(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=20)
        self.value = None

    @nextcord.ui.button(label='Playlist', style=nextcord.ButtonStyle.blurple)
    async def playlist(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = 1
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()

    @nextcord.ui.button(label='Song', style=nextcord.ButtonStyle.blurple)
    async def song(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = 2
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()
