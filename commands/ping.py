from parsing import Flags
from log import conditional_log
from discord.ext.commands import param
import json
from .shared import uses_flags

with open('commands/ping.json') as f:
    __data = json.load(f)
name = 'ping'
params = __data['params']
description = __data['description']
logs = __data['logs']

@uses_flags
async def func(ctx, _: dict[str, str], flags: Flags):
    if flags is not None and flags['help']:
        await ctx.send(logs['-h'])
        return
    await conditional_log(ctx, flags, 'pong', important=True)
    await conditional_log(ctx, flags, 'verbose pong')