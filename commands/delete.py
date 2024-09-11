from discord.ext.commands import param
from parsing import parse_time, parse_flexible_time
from log import conditional_log
import json
from parsing import Flags, FORMAT as TIME_FORMAT
from .shared import uses_flags, has_help
from datetime import datetime

with open('commands/delete.json') as f:
    __data = json.load(f)
name = 'delete'
params = __data['params']
description = __data['description']
logs = __data['logs']

@uses_flags
@has_help(logs['-h'])
async def func(ctx, params: str, flags: Flags):
    start_date = params.get('start_date', None)
    end_date = params.get('end_date', None)
    
    # Convert date strings to datetime objects
    try:
        if start_date is None:
            start_datetime = ctx.channel.created_at
            start_date = start_datetime.strftime(TIME_FORMAT)
        else:
            start_datetime = parse_time(start_date)
        if end_date is None:
            end_datetime = datetime.now()
        else:
            end_datetime = parse_flexible_time(start_date, end_date)
    except ValueError:
        await conditional_log(ctx, flags, logs['invalid-date'], important=True)
    
    messages = [message async for message in ctx.channel.history(limit=None, after=start_datetime, before=end_datetime)]
    await conditional_log(ctx, flags, logs['fetch'].format(len(messages), start_date, end_date))
    
    # Delete messages
    for message in messages:
        await message.delete()
        await conditional_log(ctx, flags, logs['delete'].format(message.id))
    
    await conditional_log(ctx, flags, logs['finish'].format(start_date, end_date))