import os
import nextcord
from nextcord.ext import commands
import sys
import configgen
import os.path
from nextcord import Interaction
os.system("clear")

configgen.generateConfiguration('m!', True, 'TOKEN', 'TOKEN')
import config
Token = config.Token
extensions = config.extension
seanToken = config.seanToken

intents = nextcord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=extensions, intents=intents, help_command=None, case_insensitive=True)

if Token == 'TOKEN':
    sys.exit("Please put your Bot's Token in the config.py file")

pwd = os.path.dirname(os.path.realpath(__file__))

@client.event
async def on_ready():
    game = config.extension + 'help'
    activity = nextcord.Game(name=game, type=3)
    await client.change_presence(status=nextcord.Status.online, activity=activity)
    print('We have logged in as {0.user}\n'.format(client))

extensions = []

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        extensions.append("cogs." + filename[:-3])

if __name__ == '__main__':
    for extension in extensions:
        client.load_extension(extension)

client.run(Token)