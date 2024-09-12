from parsing import Flags
from log import conditional_log
import json
from .shared import command, get_message_generator_by_ids, delete_message

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
    ids = ids.split(',')
    
    message_generator = get_message_generator_by_ids(ctx, flags, ids)
    async for message in message_generator:
        await delete_message(ctx, flags, message)
    
    await conditional_log(ctx, flags, logs['finish'])
