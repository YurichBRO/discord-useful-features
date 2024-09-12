from parsing import Flags
from log import conditional_log
import json
from .shared import command

with open('commands/delete_threads.json') as f:
    __data = json.load(f)
name = 'delete_threads'
params = __data['params']
description = __data['description']
logs = __data['logs']

@command({
    "thread_names": None,
    "all_occurences": "false",
}, logs['-h'])
async def func(ctx, params: list, flags: Flags):
    thread_names, all_occurences = params
    thread_names = set(thread_names.split(','))
    all_occurences = all_occurences.lower() == 'true'
    not_found = thread_names.copy()
    count = 0
    
    for thread in ctx.channel.threads:
        if thread.name not in thread_names:
            continue
        if not all_occurences:
            thread_names.remove(thread.name)
        if thread.name in not_found:
            not_found.remove(thread.name)
        count += 1
        await thread.delete()
        await conditional_log(ctx, flags, logs['deleted'].format(thread.name))
    
    if not not_found:
        await conditional_log(ctx, flags, logs["finish"].format(count))
        return
    
    for thread_name in not_found:
        await conditional_log(ctx, flags, logs["not-found"].format(thread_name), important=True)