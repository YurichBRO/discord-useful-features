import discord
from time_parsing import parse_time
from flags import parse, Flags
from log import conditional_log, flags_missing
from discord.ext.commands import param
import json

with open('commands/reloc.json') as f:
    __data = json.load(f)
name = 'reloc'
params = __data['params']
description = __data['description']
logs = __data['logs']

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

archive_duration_syntaxes = {
    60: ["h", "1h", "hour", "1hour"],
    1440: ["d", "1d", "day", "1day"],
    4320: ["3d", "3days", "3day"],
    10080: ["7d", "7days", "7day", "w", "week", "1week"],
}

def archive_duration_to_minutes(archive_in: str):
    try:
        return int(archive_in)
    except ValueError:
        pass
    for minutes, syntaxes in archive_duration_syntaxes.items():
        if archive_in in syntaxes:
            return minutes
    raise ValueError(f"invalid archive_in: {archive_in}")

async def func(ctx,
               flags: str | None = param(description=params['flags']),
               thread_name: str | None = param(description=params['thread_name']),
               start_date: str | None = param(description=params['start_date']),
               end_date: str | None = param(description=params['end_date']),
               archive_in: str | None = param(description=params['archive_in'], default="60")):
    if flags == None:
        await flags_missing(ctx)
        return
    try:
        flags = await parse(ctx, flags)
    except ValueError:
        return
    if flags['help']:
        await conditional_log(ctx, flags, logs['-h'], important=True)
        return
    if thread_name is None:
        await conditional_log(ctx, flags, logs['no-thread'], important=True)
        return
    if start_date is None or end_date is None:
        await conditional_log(ctx, flags, logs['no-date'], important=True)
        return
    # Convert date strings to datetime objects
    try:
        start_datetime = parse_time(start_date)
        end_datetime = parse_time(end_date)
    except:
        await conditional_log(ctx, flags, logs['invalid-date'], important=True)
        return
    
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
    messages = [message async for message in ctx.channel.history(limit=None, after=start_datetime, before=end_datetime)]
    await conditional_log(ctx, flags, logs['fetch'].format(len(messages), start_date, end_date))

    # Re-send messages in the new thread
    for message in messages:
        await resend_to(ctx, flags, thread, message)
        
    await conditional_log(ctx, flags, logs['finish'].format(start_date, end_date, thread.mention))