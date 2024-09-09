import discord
from parsing import parse_time
from parsing import Flags
from log import conditional_log
from discord.ext.commands import param
import json
from .shared import uses_flags, archive_duration_to_minutes, get_parent, resend_to

with open('commands/reloc_id.json') as f:
    __data = json.load(f)
name = 'reloc_id'
params = __data['params']
description = __data['description']
logs = __data['logs']

@uses_flags
async def func(ctx, params: dict[str, str], flags: Flags):
    if flags is not None and flags['help']:
        await ctx.send(logs['-h'])
        return
    
    thread_name = params.get("thread_name", None)
    ids = params.get("ids", None)
    archive_in = params.get("archive_in", "60")
    title = params.get("title", "true")
    
    if thread_name is None:
        await conditional_log(ctx, flags, logs['no-thread'], important=True)
        return
    if ids is None:
        await conditional_log(ctx, flags, logs['no-ids'], important=True)
        return
    
    ids = ids.split('-')
    
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
    messages = [await ctx.channel.fetch_message(id) for id in ids]
    await conditional_log(ctx, flags, logs['fetch'].format(len(messages)))

    # Re-send messages in the new thread
    for message in messages:
        await resend_to(ctx, flags, thread, message, title=title == "true")
        
    await conditional_log(ctx, flags, logs['finish'].format(thread.mention))