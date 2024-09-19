from parsing import Flags
from log import conditional_log
from shared import command

data = {
    "name": "ping",
    "description": "ping pong",
}

@command(data)
async def func(ctx, _: list, flags: Flags):
    await conditional_log(ctx, flags, 'pong', important=True)
    await conditional_log(ctx, flags, 'verbose pong')