from flags import Flags
from log import conditional_log
from discord.ext.commands import param
import json
from .shared import uses_flags, has_help_flag

with open('commands/ping.json') as f:
    __data = json.load(f)
name = 'ping'
params = __data['params']
description = __data['description']
logs = __data['logs']

@uses_flags
@has_help_flag(logs['-h'])
async def func(ctx, flags: str | None):
    await conditional_log(ctx, flags, 'pong', important=True)
    await conditional_log(ctx, flags, 'verbose pong')