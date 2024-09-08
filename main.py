import discord
from discord.ext import commands
from commands import ping, reloc, delete, reloc_id
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
bot = commands.Bot(command_prefix='/', intents=intents) 

for module in [ping, reloc, delete, reloc_id]:
    commandify(bot, module)

bot.run(TOKEN)