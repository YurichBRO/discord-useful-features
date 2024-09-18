import discord
import commands
from discord.ext import commands as discord_commands
from help import help_string

from dotenv import load_dotenv
from os import getenv

def commandify(bot, func, data):
    name = data['name']
    description = data['description']
    bot.command(name=name, description=description)(func)

result = load_dotenv('.env')
if not result:
    raise Exception('Failed to load .env')
TOKEN = getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = discord_commands.Bot(command_prefix='/', intents=intents, help_command=None)
 
def get_user_attributes(obj):
    for attr in dir(obj):
        if not attr.startswith('__'):
            yield attr

for module_name in get_user_attributes(commands):
    module = getattr(commands, module_name)
    func = module.func
    data = module.data
    commandify(bot, func, data)

# help is already defined in commands/help.py. We replace placeholder with an actual command here
bot.remove_command('help')
@bot.command()
async def help(ctx, command_name: str | None):
    if not command_name:
        await ctx.send(f"""```To get help on a specific command, use the command `/help <command_name>`.

Available commands:
    {'\n    '.join(map(lambda command_name: getattr(commands, command_name).data['name'], get_user_attributes(commands)))}
```""")
        return
    command = command_name.lower()
    if hasattr(commands, command):
        command_module = getattr(commands, command)
        command_data = command_module.data
        uses_decorator = command_data.get('uses-decorator', True)
        if uses_decorator:
            await ctx.send(help_string(command_data))
        else:
            description = command_data.get('description', "Description is not provided")
            await ctx.send(f"```{description}```")
    else:
        await ctx.send(f"Command '{command_name}' does not exist")



bot.run(TOKEN)