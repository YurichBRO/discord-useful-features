import discord
from discord.ext import commands
from datetime import datetime
from commands import ping, reloc, delete
from dotenv import load_dotenv
from os import getenv
'''
def commandified(bot, function, **kwargs):
    bot.command(**kwargs)(function)

def commandify(bot, functions: dict[callable, dict[str, any]]):
    for function, kwargs in functions.items():
        commandified(bot, function, **kwargs)
'''

def commandify(bot, module):
    bot.command(name=module.name, help=module.description)(module.func)

result = load_dotenv('.env')
if not result:
    raise Exception('Failed to load .env')
TOKEN = getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents) 

for module in [ping, reloc, delete]:
    commandify(bot, module)

bot.run(TOKEN)