from parsing import parse_time, parse_flexible_time
from parsing import Flags, FORMAT as TIME_FORMAT
from log import conditional_log
import json
from .shared import command, archive_duration_to_minutes, get_parent, has_help, resend_messages_to
from datetime import datetime

with open('commands/reloc.json') as f:
    __data = json.load(f)
name = 'reloc'
params = __data['params']
description = __data['description']
logs = __data['logs']

@command({
    "thread_name": None,
    "start_date": "",
    "end_date": "",
    "archive_in": "60",
    "title": "true",
    "delete": "false",
}, logs['-h'])
async def func(ctx, params: list, flags: Flags):
    thread_name, start_date, end_date, archive_in, title, delete = params
    
    if thread_name is None:
        await conditional_log(ctx, flags, logs['no-thread'], important=True)
        return
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
        return
    
    try:
        archive_in = archive_duration_to_minutes(archive_in)
    except:
        await conditional_log(ctx, flags, logs['invalid-archive-in'], important=True)
        return
    
    channel = get_parent(ctx.channel)
    if thread_name == "-":
        thread = channel
        await conditional_log(ctx, flags, logs['using-channel'].format(channel.mention))
    else:
        thread = await channel.create_thread(name=thread_name, auto_archive_duration=archive_in)
        await conditional_log(ctx, flags, logs['create-thread'].format(thread.mention))

    # Fetch messages from the channel
    messages = [message async for message in ctx.channel.history(limit=None, after=start_datetime, before=end_datetime)]
    await conditional_log(ctx, flags, logs['fetch'].format(len(messages), start_date, end_date))

    # Re-send messages in the new thread
    await resend_messages_to(ctx, flags, thread, messages, title=title == "true", delete=delete == "true")
        
    await conditional_log(ctx, flags, logs['finish'].format(start_date, end_date, thread.mention))