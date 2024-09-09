import discord
import commands
from discord.ext import commands as discord_commands

from dotenv import load_dotenv
from os import getenv

def commandify(bot, module):
    bot.command(name=module.name, help=module.description)(module.func)

result = load_dotenv('.env')
if not result:
    raise Exception('Failed to load .env')
TOKEN = getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = discord_commands.Bot(command_prefix='/', intents=intents) 

for module_name in commands.__all__:
    module = getattr(commands, module_name)
    commandify(bot, module)

bot.run(TOKEN)