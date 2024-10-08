from parsing import Flags
from log import conditional_log
from shared import command, archive_duration_to_minutes, get_parent, resend_to, uses_selection
from datetime import datetime
from .select import SELECTED_MESSAGES_FILE

data = {
    "name": "reloc",
    "description": "Relocates selected messages to a new thread",
    "params": {
        "thread_name": {
            "description": "Name of the new thread",
            "required": True
        },
        "archive_in": {
            "description": "Time in minutes to archive the thread after",
            "required": False,
            "default": "60"
        },
        "title": {
            "description": "Whether to add title to the message or not",
            "required": False,
            "default": "true"
        },
        "delete": {
            "description": "Whether to delete the original message or not",
            "required": False,
            "default": "false"
        }
    }
}

@command(data)
@uses_selection(SELECTED_MESSAGES_FILE)
async def func(ctx, params: list, flags: Flags, selected_messages: list[int]):
    thread_name, archive_in, title, delete = params
    
    try:
        archive_in = archive_duration_to_minutes(archive_in)
    except:
        await conditional_log(ctx, flags, "Invalid archive_in value, should be 60, 1440, 4320, 10080", important=True)
        return
    
    title = title.lower() == "true"
    delete = delete.lower() == "true"
    
    channel = get_parent(ctx.channel)
    if thread_name == "-":
        thread = channel
        await conditional_log(ctx, flags, f"Using current channel {channel.mention} as thread.")
    else:
        thread = await channel.create_thread(name=thread_name, auto_archive_duration=archive_in)
        await conditional_log(ctx, flags, f"Created thread {thread.mention}.")

    # Fetch messages from the channel
    for id in selected_messages:
        try:
            message = await ctx.channel.fetch_message(id)
            await resend_to(ctx, flags, thread, message, title, delete)
        except:
            await conditional_log(ctx, flags, f"could not fetch message {id}", important=True)
        
    await conditional_log(ctx, flags, f"Messages have been relocated to the new thread: {thread.mention}")