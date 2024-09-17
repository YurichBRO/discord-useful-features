from log import conditional_log
import json
from parsing import Flags, FORMAT as TIME_FORMAT
from .shared import command, delete_message, uses_selection
from datetime import datetime
from .select import SELECTED_MESSAGES_FILE

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
@uses_selection(SELECTED_MESSAGES_FILE)
async def func(ctx, params: list, flags: Flags, selected_messages: list[int]):
    for id in selected_messages:
        try:
            message = await ctx.channel.fetch_message(id)
            await delete_message(ctx, flags, message)
        except:
            await conditional_log(ctx, flags, f"could not fetch message {id}", important=True)
    
    await conditional_log(ctx, flags, logs['finish'])