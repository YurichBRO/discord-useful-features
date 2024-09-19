from parsing import Flags
from log import conditional_log
from shared import command, uses_selection
from .select_threads import SELECTED_THREADS_FILE

data = {
    "name": "delete_threads",
    "description": "Deletes selected threads",
}

@command(data)
@uses_selection(SELECTED_THREADS_FILE)
async def func(ctx, params: list, flags: Flags, selected_threads: list[int]):
    count = 0
    
    for id in selected_threads:
        try:
            thread = ctx.channel.get_thread(id)
            await thread.delete()
            await conditional_log(ctx, flags, f"deleted thread {id}")
            count += 1
        except:
            await conditional_log(ctx, flags, f"could not fetch thread {id}", important=True)
    await conditional_log(ctx, flags, f"Deleted {count} threads")