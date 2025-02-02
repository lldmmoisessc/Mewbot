# The Halls.py Cog handles all the commands related to the Halls functionality (starboard?)
from Dependencies.Functions import Color
from datetime import datetime
from datetime import UTC
import nextcord
from nextcord.ext import commands, tasks
from nextcord import Interaction
import settings
import Dependencies.SQLFunc as SQLFunc
from Dependencies.Error import ReconnectError
import asyncio


class Halls(commands.Cog):

    def __init__(self, client):
        print("Halls Initialized Successfully")
        self.client = client
        self.hallscheck.start()

    # Checks for new halls every five minutes when the bot is first started up, after that, it checks every hour
    @tasks.loop(minutes=5)
    async def hallscheck(self):

        # Waits if the Bot is ready to start hall check
        await self.client.wait_until_ready()

        # Sets the interval to 1 hour after 5 checks
        if self.hallscheck.current_loop == 5:
            self.hallscheck.change_interval(hours=1)
        for guild in self.client.guilds:

            # Checks if there is an SQL connection still active
            try:
                await SQLFunc.checkConn()
            except ReconnectError:
                print(f"{Color.RED}{Color.BOLD}SQL Connection Lost. Will attempt to check halls later{Color.END}")
                return

            # Sets up SQL cursor and checks the message history for halls
            settings.connection.commit()
            cursor = settings.connection.cursor(dictionary=True, buffered=True)
            cursor.execute(f"""SELECT * FROM {guild.id}_Halls""")
            records = cursor.fetchall()
            for record in records:
                await SQLFunc.historycheck(guild, record['Channel'], record['Hall'], record['Amount'],
                                           record['Emote'], record['Hall_Emote'])
        print(f"Halls Check Finished at {Color.DARKCYAN}{Color.BOLD}{datetime.now(UTC)}{Color.END}")

    # The halllist command lists all the halls in the current guild
    @nextcord.slash_command(name="halllist",
                            description="Prints the current Guild's Halls")
    async def halllist(self, interaction: Interaction):

        # Checks if there is an SQL connection still active
        try:
            await SQLFunc.checkConn()
        except ReconnectError:
            embed = nextcord.Embed(title='Failed to Connect to the SQL Server', description='Please Try Again Later.')
            await interaction.send(embed=embed)
            return

        # First it ensures that its information is updated and sets up a cursor
        settings.connection.commit()
        cursor = settings.connection.cursor(dictionary=True, buffered=True)

        # It then queries the Database to grab all entries for the current guild
        cursor.execute(f"SELECT * FROM {interaction.guild.id}_Halls")
        records = cursor.fetchall()

        # It then embeds them, sends them to the current guild, and closes the cursor
        embed = nextcord.Embed(title=f"{interaction.guild.name}'s Halls")

        # Iterates through database records and prints all the halls for the current server
        for row in records:
            embed.add_field(name="",
                            value=f"<#{row['Channel']}>{row['Emote']}x{row['Amount']} >> <#{row['Hall']}>{row['Hall_Emote']}",
                            inline=False)
        await interaction.send(embed=embed)
        cursor.close()

    # The hall command adds a hall to the current guild's database
    @nextcord.slash_command(name="hall",
                            description="Updates or Adds a Hall. Note: Hall emote is to prevent spam by adding the "
                                        "emote when a hall is added")
    async def hall(self, interaction: Interaction, channel: str, emote: str, amount: int, hall: str, hall_emote: str):

        # First it strips the string to ensure it is in the right format
        channel = channel.lstrip('<#')
        channel = channel.rstrip('>')
        hall = hall.lstrip('<#')
        hall = hall.rstrip('>')
        channel = "".join(c for c in channel if c.isnumeric())
        hall = "".join(c for c in hall if c.isnumeric())

        # Then it ensures that the channels provided aren't invalid or duplicates
        if not interaction.guild.get_channel(int(channel)) or not interaction.guild.get_channel(int(hall)):
            await interaction.send("Invalid Channel or Hall Channel Provided")
            return
        elif channel == hall:
            await interaction.send("Channel cannot be its own Hall")
            return

        # It also makes sure that the emote and the Hall_Emote is valid in the current server
        emojis = await interaction.guild.fetch_emojis()
        emotefound = False
        hallemotef = False
        for emoji in emojis:
            if str(emoji.id) in emote:
                emotefound = emoji.id
                emote = str(emoji)
            if str(emoji.id) in hall_emote:
                hallemotef = emoji.id
                hall_emote = str(emoji)
        if not emotefound or not hallemotef:
            await interaction.send("Invalid Emoji Provided, Please provide a server Emoji")
            return
        elif emotefound == hallemotef:
            await interaction.send("Hall Emoji and Emoji can't be the same")
            return

        # Checks if there is an SQL connection still active
        try:
            await SQLFunc.checkConn()
        except ReconnectError:
            embed = nextcord.Embed(title='Failed to Connect to the SQL Server', description='Please Try Again Later.')
            await interaction.send(embed=embed)
            return

        # Sets up the connection to the database and sets up the cursor
        settings.connection.commit()
        cursor = settings.connection.cursor(dictionary=True, buffered=True)

        # This ensures that person running the command is allowed to
        if not await SQLFunc.rolecheck(interaction):
            return

        # It sets up the database connection and cursor, where it queries to make sure the hall exists or not
        # It also grabs the entire table of Halls for the guild
        cursor.execute(f"SELECT * FROM {interaction.guild.id}_Halls WHERE Channel = {channel}")
        record = cursor.fetchall()
        cursor.execute(f"SELECT * FROM {interaction.guild.id}_Halls")
        table = cursor.fetchall()

        # Using the table of halls, it makes sure that a Hall Channel isn't a main channel
        for entry in table:
            if hall in entry['Channel'] or channel in entry['Hall']:
                await interaction.send("Hall Channel cannot be another Hall Entry")
                return

        # If the hall exists, then it queries the database to update it with the information provided
        if record:
            await interaction.send(f"Hall found, Updating according to the following specifications:\n" +
                                   f"Channel: <#{channel}>\nEmote: {emote}\nAmount: {amount}\nHall: <#{hall}>\n " +
                                   f"Hall_emote: {hall_emote}")
            cursor.execute(f"""UPDATE {interaction.guild.id}_Halls SET
                            Emote = '{emote}',
                            Amount = {amount},
                            Hall = '{hall}', 
                            Hall_Emote = '{hall_emote}' WHERE
                            Channel = '{channel}'""")

        # If not, then the database is queried to make a new record for the hall in the guild's database
        else:
            await interaction.send(f"Hall not found, adding according to the following specifications:\n" +
                                   f"Channel: <#{channel}>\nEmote: {emote}\nAmount: {amount}\nHall: <#{hall}>\n " +
                                   f"Hall_emote: {hall_emote}")
            cursor.execute(f"""INSERT INTO {interaction.guild.id}_Halls
                            (Channel, Emote, Amount, Hall, Hall_Emote) VALUES
                            ('{channel}', '{emote}', {amount}, '{hall}', '{hall_emote}')""")

        # It then commits the changes and closes the cursor
        settings.connection.commit()
        cursor.close()

        # Checks older messages for a hall
        await SQLFunc.historycheck(interaction.guild, channel, hall, amount, emote, hall_emote)

    # The remove hall command removes a single hall from the database
    @nextcord.slash_command(name="removehall",
                            description="Removes a Hall")
    async def removehall(self, interaction: Interaction, channel: str, ):

        # First it strips the string to ensure it is in the proper format
        channel = channel.lstrip('<#')
        channel = channel.rstrip('>')
        channel = "".join(c for c in channel if c.isnumeric())

        # Then it makes sure that the channel provided is a valid channel
        if not interaction.guild.get_channel(int(channel)):
            await interaction.send("Invalid Channel or Hall Channel Provided")
            return

        # Checks if there is an SQL connection still active
        try:
            await SQLFunc.checkConn()
        except ReconnectError:
            embed = nextcord.Embed(title='Failed to Connect to the SQL Server', description='Please Try Again Later.')
            await interaction.send(embed=embed)
            return

        # It then prepares the database
        settings.connection.commit()
        cursor = settings.connection.cursor(dictionary=True, buffered=True)

        # This ensures that person running the command is allowed to
        if not await SQLFunc.rolecheck(interaction):
            return

        # checks to make sure that the hall exists
        cursor.execute(f"SELECT * FROM {interaction.guild.id}_Halls WHERE Channel = {channel}")
        record = cursor.fetchall()

        # If it doesn't exist, then it lets the user know and exits the function
        if not record:
            await interaction.send(f"No Hall with channel <#{channel}>")
            return

        # If it does exist, it deletes it from the database, lets the user know, updates the database
        # Finally, it closes the cursor to clean up
        cursor.execute(f"DELETE FROM {interaction.guild.id}_Halls WHERE Channel = {channel}")
        await interaction.send(f"Deleted Hall associated with channel <#{channel}>")
        settings.connection.commit()
        cursor.close()

    # on_message listens for messages coming in to make sure if they have attachments or embeds
    @commands.Cog.listener()
    async def on_message(self, message):

        # First it ensures that the message isn't a message from itself
        if message.author == self.client.user:
            return

        # It then waits to ensure that the message being checked has an embed that hasn't populated yet
        await asyncio.sleep(2)

        # Then it updates the database and sets up a cursor to make a query for that specific channel
        record = None
        if message.guild:

            # Checks if there is an SQL connection still active
            try:
                await SQLFunc.checkConn()
            except ReconnectError:
                return

            # Then it sets up an SQL server which checks if the message is in a hall channel
            settings.connection.commit()
            cursor = settings.connection.cursor(dictionary=True, buffered=True)
            cursor.execute(f"SELECT * FROM {message.guild.id}_Halls WHERE Channel = '{message.channel.id}'")
            record = cursor.fetchone()

        # If the record for the channel exists and checks for attachments or embeds, then it adds the emote
        if record and (message.attachments or message.embeds):
            await message.add_reaction(record['Emote'])

    # On_reaction_add listens for emotes to send items to halls
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):

        # Checks if a message has attachments or embeds
        if reaction.message.attachments or reaction.message.embeds:

            # Checks if there is an SQL connection still active
            try:
                await SQLFunc.checkConn()
            except ReconnectError:
                return

            # Updates the database and sets up a cursor to make a query for that specfic channel
            settings.connection.commit()
            cursor = settings.connection.cursor(dictionary=True, buffered=True)
            cursor.execute(
                f"SELECT * FROM {reaction.message.guild.id}_Halls WHERE Channel = '{reaction.message.channel.id}'")
            record = cursor.fetchone()

            # Checks if the emote is in the message and if the count is greater than or equal to the amount necessary
            # for a hall
            if record:
                if record['Emote'] == str(reaction) and reaction.count >= record['Amount']:

                    # Checks to make sure it isn't in a hall yet
                    for emote in reaction.message.reactions:
                        if str(emote) == record['Hall_Emote'] and emote.me:
                            return

                    # if it isn't, then it grabs the channel and sends it to the hall
                    channel = nextcord.utils.get(reaction.message.guild.channels, id=int(record['Hall']))
                    await SQLFunc.halladd(reaction.message, channel, record['Hall_Emote'])


def setup(client):
    client.add_cog(Halls(client))
