from discord.ext.commands import param
from parsing import parse_time
from log import conditional_log
import json
from parsing import Flags
from .shared import uses_flags

with open('commands/delete.json') as f:
    __data = json.load(f)
name = 'delete'
params = __data['params']
description = __data['description']
logs = __data['logs']

@uses_flags
async def func(ctx, params: str, flags: Flags):
    if flags is not None and flags['help']:
        await ctx.send(logs['-h'])
        return
    
    start_date = params.get('start_date')
    if start_date is None:
        await conditional_log(ctx, flags, logs['no-date'], important=True)
        return
    end_date = params.get('end_date')
    if end_date is None:
        await conditional_log(ctx, flags, logs['no-date'], important=True)
        return
    
    # Convert date strings to datetime objects
    try:
        start_datetime = parse_time(start_date)
        end_datetime = parse_time(end_date)
    except ValueError:
        await conditional_log(ctx, flags, logs['invalid-date'], important=True)
    
    messages = [message async for message in ctx.channel.history(limit=None, after=start_datetime, before=end_datetime)]
    await conditional_log(ctx, flags, logs['fetch'].format(len(messages), start_date, end_date))
    
    # Delete messages
    for message in messages:
        await message.delete()
        await conditional_log(ctx, flags, logs['delete'].format(message.id))
    
    await conditional_log(ctx, flags, logs['finish'].format(start_date, end_date))