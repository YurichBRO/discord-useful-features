from parsing import Flags
from log import conditional_log
import json
from .shared import command, archive_duration_to_minutes, get_parent, resend_to, uses_selection
from datetime import datetime
from .select import SELECTED_MESSAGES_FILE

with open('commands/reloc.json') as f:
    __data = json.load(f)
name = 'reloc'
params = __data['params']
description = __data['description']
logs = __data['logs']

@command({
    "thread_name": None,
    "archive_in": "60",
    "title": "true",
    "delete": "false",
}, logs['-h'])
@uses_selection(SELECTED_MESSAGES_FILE)
async def func(ctx, params: list, flags: Flags, selected_messages: list[int]):
    thread_name, archive_in, title, delete = params
    
    try:
        archive_in = archive_duration_to_minutes(archive_in)
    except:
        await conditional_log(ctx, flags, logs['invalid-archive-in'], important=True)
        return
    
    title = title.lower() == "true"
    delete = delete.lower() == "true"
    
    channel = get_parent(ctx.channel)
    if thread_name == "-":
        thread = channel
        await conditional_log(ctx, flags, logs['using-channel'].format(channel.mention))
    else:
        thread = await channel.create_thread(name=thread_name, auto_archive_duration=archive_in)
        await conditional_log(ctx, flags, logs['create-thread'].format(thread.mention))

    # Fetch messages from the channel
    for id in selected_messages:
        try:
            message = await ctx.channel.fetch_message(id)
            await resend_to(ctx, flags, thread, message, title, delete)
        except:
            await conditional_log(ctx, flags, f"could not fetch message {id}", important=True)
        
    await conditional_log(ctx, flags, logs['finish'].format(thread.mention))