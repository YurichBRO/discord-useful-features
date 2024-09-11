from parsing import Flags
from log import conditional_log
from discord.ext.commands import param
import json
from .shared import uses_flags, uses_params, has_help

with open('commands/ping.json') as f:
    __data = json.load(f)
name = 'ping'
params = __data['params']
description = __data['description']
logs = __data['logs']

@uses_params
@uses_flags
@has_help(logs['-h'])
async def func(ctx, _: dict[str, str], flags: Flags):
    await conditional_log(ctx, flags, 'pong', important=True)
    await conditional_log(ctx, flags, 'verbose pong')