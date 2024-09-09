import discord
from parsing import parse_time, parse_flexible_time
from parsing import Flags
from log import conditional_log
from discord.ext.commands import param
import json
from .shared import uses_flags, archive_duration_to_minutes, get_parent, resend_to, has_help

with open('commands/reloc.json') as f:
    __data = json.load(f)
name = 'reloc'
params = __data['params']
description = __data['description']
logs = __data['logs']

@uses_flags
@has_help(logs['-h'])
async def func(ctx, params: dict[str, str], flags: Flags):
    thread_name = params.get("thread_name", None)
    start_date = params.get("start_date", None)
    end_date = params.get("end_date", None)
    archive_in = params.get("archive_in", "60")
    title = params.get("title", "true")
    delete = params.get("delete", "false")
    
    if thread_name is None:
        await conditional_log(ctx, flags, logs['no-thread'], important=True)
        return
    if start_date is None or end_date is None:
        await conditional_log(ctx, flags, logs['no-date'], important=True)
        return
    # Convert date strings to datetime objects
    try:
        start_datetime = parse_time(start_date)
        end_datetime = parse_flexible_time(start_date, end_date)
    except:
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
    for message in messages:
        await resend_to(ctx, flags, thread, message, title=title == "true", delete=delete == "true")
        
    await conditional_log(ctx, flags, logs['finish'].format(start_date, end_date, thread.mention))