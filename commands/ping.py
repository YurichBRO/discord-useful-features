from flags import parse
from log import conditional_log, flags_missing
from discord.ext.commands import param
import json

with open('commands/ping.json') as f:
    __help = json.load(f)
name = 'ping'
params = __help['params']
description = __help['description']

async def func(ctx, flags: str | None = param(description=params['flags'])):
    if flags == None:
        await flags_missing(ctx)
        return
    try:
        flags = await parse(ctx, flags)
    except ValueError:
        return
    if flags['help']:
        await conditional_log(ctx, flags, "Usage: `/ping -[flags]`", important=True)
        return
    await conditional_log(ctx, flags, 'pong', important=True)
    await conditional_log(ctx, flags, 'verbose pong')