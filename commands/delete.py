from parsing import parse_time, parse_flexible_time
from log import conditional_log
import json
from parsing import Flags, FORMAT as TIME_FORMAT
from .shared import command, delete_message, get_message_generator_by_time
from datetime import datetime

with open('commands/delete.json') as f:
    __data = json.load(f)
name = 'delete'
params = __data['params']
description = __data['description']
logs = __data['logs']

@command({
    "start_date": "",
    "end_date": "",
}, logs['-h'])
async def func(ctx, params: list, flags: Flags):
    start_date, end_date = params
    
    # Convert date strings to datetime objects
    try:
        if not start_date:
            start_datetime = ctx.channel.created_at
            start_date = start_datetime.strftime(TIME_FORMAT)
        else:
            start_datetime = parse_time(start_date)
        if not end_date:
            end_datetime = datetime.now()
        else:
            end_datetime = parse_flexible_time(start_date, end_date)
    except ValueError:
        await conditional_log(ctx, flags, logs['invalid-date'], important=True)
    
    message_generator = get_message_generator_by_time(ctx, flags, start_datetime, end_datetime)
    async for message in message_generator:
        await delete_message(ctx, flags, message)
    
    await conditional_log(ctx, flags, logs['finish'].format(start_date, end_date))