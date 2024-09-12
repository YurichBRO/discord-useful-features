from parsing import Flags
from log import conditional_log
import json
from .shared import command

with open('commands/ping.json') as f:
    __data = json.load(f)
name = 'ping'
params = __data['params']
description = __data['description']
logs = __data['logs']

@command({}, logs['-h'])
async def func(ctx, _: list, flags: Flags):
    await conditional_log(ctx, flags, 'pong', important=True)
    await conditional_log(ctx, flags, 'verbose pong')