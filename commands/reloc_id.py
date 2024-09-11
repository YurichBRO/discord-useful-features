from parsing import Flags
from log import conditional_log
import json
from .shared import command, archive_duration_to_minutes, get_parent, resend_to, has_help, resend_messages_to

with open('commands/reloc_id.json') as f:
    __data = json.load(f)
name = 'reloc_id'
params = __data['params']
description = __data['description']
logs = __data['logs']

@command({
    "thread_name": None,
    "ids": None,
    "archive_in": "60",
    "title": "true",
    "delete": "false",
}, logs['-h'])
async def func(ctx, params: list, flags: Flags):
    thread_name, ids, archive_in, title, delete = params
    
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
    messages = []
    for id in ids:
        try:
            message = await ctx.channel.fetch_message(int(id))
            messages.append(message)
        except:
            await conditional_log(ctx, flags, logs['not-found'].format(id), important=True)
            return
    await conditional_log(ctx, flags, logs['fetch'].format(len(messages)))

    # Re-send messages in the new thread
    await resend_messages_to(ctx, flags, thread, messages, title=title == "true", delete=delete == "true")
        
    await conditional_log(ctx, flags, logs['finish'].format(thread.mention))