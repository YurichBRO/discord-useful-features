from parsing import Flags
from log import conditional_log
import json
from .shared import command, archive_duration_to_minutes, get_parent, get_message_generator_by_ids, resend_to

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
    
    ids = [int(i) for i in ids.split(',')]
    try:
        archive_in = archive_duration_to_minutes(archive_in)
    except:
        await conditional_log(ctx, flags, logs['invalid-archive-in'], important=True)
        return
    title = title == "true"
    delete = delete == "true"
    
    channel = get_parent(ctx.channel)
    if thread_name == "-":
        thread = channel
        await conditional_log(ctx, flags, logs['using-channel'].format(channel.mention))
    else:
        thread = await channel.create_thread(name=thread_name, auto_archive_duration=archive_in)
        await conditional_log(ctx, flags, logs['create-thread'].format(thread.mention))
    
    message_generator = get_message_generator_by_ids(ctx, flags, ids)
    async for message in message_generator:
        await resend_to(ctx, flags, thread, message, title, delete)
        
    await conditional_log(ctx, flags, logs['finish'].format(thread.mention))