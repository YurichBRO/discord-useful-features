from discord.ext.commands import param
from time_parsing import parse_time
from flags import parse
from log import conditional_log, flags_missing
import json

with open('commands/delete.json') as f:
    __data = json.load(f)
name = 'delete'
params = __data['params']
description = __data['description']
logs = __data['logs']

async def func(ctx,
                 flags: str | None = param(description=params['flags']),
                 start_date: str | None = param(description=params['start_date']),
                 end_date: str | None = param(description=params['end_date'])):
    if flags == None:
        await flags_missing(ctx)
        return
    try:
        flags = await parse(ctx, flags)
    except ValueError:
        return
    if flags['help']:
        await conditional_log(ctx, flags, logs['-h'], important=True)
        return
    if start_date is None or end_date is None:
        await conditional_log(ctx, flags, logs['no-date'], important=True)
        return
    # Convert date strings to datetime objects
    try:
        start_datetime = parse_time(start_date)
        end_datetime = parse_time(end_date)
    except ValueError:
        await conditional_log(ctx, flags, logs['invalid-date'], important=True)
        return
    
    # Fetch messages from the channel
    messages = [message async for message in ctx.channel.history(limit=None, after=start_datetime, before=end_datetime)]
    await conditional_log(ctx, flags, logs['fetch'].format(len(messages), start_date, end_date))
    
    # Delete messages
    for message in messages:
        await message.delete()
        await conditional_log(ctx, flags, logs['delete'].format(message.id))
    
    await conditional_log(ctx, flags, logs['finish'].format(start_date, end_date))