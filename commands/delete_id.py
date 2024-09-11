import discord
from parsing import Flags
from log import conditional_log
import json
from .shared import command

with open('commands/delete_id.json') as f:
    __data = json.load(f)
name = 'delete_id'
params = __data['params']
description = __data['description']
logs = __data['logs']

@command({
    "ids": None,
}, logs['-h'])
async def func(ctx, params: list, flags: Flags):
    ids = params[0]
    
    if ids is None:
        await conditional_log(ctx, flags, logs['no-ids'], important=True)
        return
    
    ids = ids.split('-')
    
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
    
    # Delete messages
    for message in messages:
        await message.delete()
        await conditional_log(ctx, flags, logs['delete'].format(message.id))
    
    await conditional_log(ctx, flags, logs['finish'].format(len(messages)))
