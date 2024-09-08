from functools import wraps
from flags import parse
import discord
from flags import Flags
from log import conditional_log

def uses_flags(func):
    @wraps(func)
    async def inner(*args):
        args = list(args)
        if len(args) == 0:
            raise ValueError("No arguments passed to function, required argument is ctx.")
        ctx = args[0]
        if len(args) < 2 or args[1] == None:
            await ctx.send("Flags parameter is required. If you don't want to use flags, use the `-` symbol as a placeholder.")
            return
        try:
            args[1] = parse(args[1])
        except ValueError as e:
            ctx.send(str(e))
        await func(*args)
    return inner

def has_help_flag(help_message):
    def outer(func):
        @wraps(func)
        async def inner(*args):
            ctx, flags = args[0], args[1]
            if flags['help']:
                await ctx.send(help_message)
                return
            await func(*args)
        return inner
    return outer

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

def get_parent(thread):
    if isinstance(thread, discord.Thread):
        return thread.parent
    else:
        return thread

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