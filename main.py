import discord
from discord.ext import commands
from datetime import datetime
from commands.ping import ping
from commands.reloc import reloc
from commands.delete import delete
from dotenv import load_dotenv
from os import getenv

def commandified(bot, function, **kwargs):
    return bot.command(**kwargs)(function)

def commandify(bot, functions: dict[callable, dict[str, any]]):
    for function, kwargs in functions.items():
        commandified(bot, function, **kwargs)

result = load_dotenv('.env')
if not result:
    raise Exception('Failed to load .env')
TOKEN = getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents) 

bot_commands = {
    ping: {
        'name': 'ping',
        'help': 'pong'
    },
    reloc: {
        'name': 'reloc',
        'help': 'relocates messages from a channel or thread to a new thread'
    },
    delete: {
        'name': 'delete',
        'help': 'deletes messages from a channel or thread'
    }
}
commandify(bot, bot_commands)

bot.run(TOKEN)