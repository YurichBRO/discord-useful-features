import discord
from time_parsing import parse_time
from flags import parse, Flags
from log import conditional_log, flags_missing

async def resend_to(ctx, flags: Flags, thread, message):
    content = message.content
    embeds = message.embeds
    files = [await file.to_file() for file in message.attachments]
    
    await thread.send(
        # the first symbol in the string is not a regular space
        f"-# **{message.author.name}** {message.created_at.strftime('%Y-%m-%d-%H:%M:%S')}:\n\t{content}",
        embeds=embeds,
        files=files
    )
    await conditional_log(ctx, flags, f"relocated message {message.id}")
    if flags['delete']:
        await message.delete()
        await conditional_log(ctx, flags, f"deleted message {message.id}")

def get_parent(thread):
    if isinstance(thread, discord.Thread):
        return thread.parent
    else:
        return thread

async def reloc(ctx,
                flags: str | None,
                thread_name: str | None,
                start_date: str | None,
                end_date: str | None):
    if flags == None:
        await flags_missing(ctx)
        return
    try:
        flags = await parse(ctx, flags)
    except ValueError:
        return
    if flags['help']:
        await conditional_log(ctx, flags, "Usage: `/reloc -[flags] [thread_name] [start_date] [end_date]`", important=True)
        return
    if thread_name is None:
        await conditional_log(ctx, flags, "Please provide a thread name.", important=True)
        return
    if start_date is None or end_date is None:
        await conditional_log(ctx, flags, "Please provide both start and end dates.", important=True)
        return
    # Convert date strings to datetime objects
    try:
        start_datetime = parse_time(start_date)
        end_datetime = parse_time(end_date)
    except:
        await conditional_log(ctx, flags, "Invalid date format.", important=True)
        return
    
    channel = get_parent(ctx.channel)
    if thread_name == "-":
        thread = channel
        await conditional_log(ctx, flags, f"Using current channel {channel.mention} as thread.")
    else:
        thread = await channel.create_thread(name=thread_name, auto_archive_duration=60)
        await conditional_log(ctx, flags, f"Created thread {thread.mention}.")

    # Fetch messages from the channel
    messages = [message async for message in ctx.channel.history(limit=None, after=start_datetime, before=end_datetime)]
    await conditional_log(ctx, flags, f"Fetched {len(messages)} messages from {start_date} to {end_date}.")

    # Re-send messages in the new thread
    for message in messages:
        await resend_to(ctx, flags, thread, message)
        
    await conditional_log(ctx, flags, f"Messages from {start_date} to {end_date} have been relocated to the new thread: {thread.mention}")