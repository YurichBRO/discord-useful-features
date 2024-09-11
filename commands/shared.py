from parsing import parse_flags, parse_params, FORMAT as TIME_FORMAT
import discord
from parsing import Flags
from log import conditional_log, log

def command(all_params: dict[str, str], help_message: str):
    def outer(func):
        async def inner(ctx, params: str | None):
            try:
                params = parse_params(params)
            except ValueError as e:
                await log(ctx, f"Could not parse params, invalid param format: {e}")
                return
            
            if "flags" not in params:
                params["flags"] = None
            flags = params["flags"]
            try:
                flags = parse_flags(flags)
            except ValueError as e:
                await log(ctx, f"Could not parse flags, invalid flags format: {e}")
                return
            del params["flags"]
            
            if flags is not None and flags['help']:
                await ctx.send(help_message)
                return
            
            for param_name in all_params:
                if param_name not in params:
                    if all_params[param_name] is None:
                        await log(ctx, f"Missing required param: {param_name}")
                        return
                    # Assigning default value in case the parameter has a default value
                    params[param_name] = all_params[param_name]
            for param_name in params:
                if param_name not in all_params:
                    await log(ctx, f"Unknown param: {param_name}")
                    return
            
            params = [params[key] for key in all_params]
            
            return await func(ctx, params, flags)
        return inner
    return outer

def uses_params(func):
    async def inner(ctx, params: str | None):
        try:
            params = parse_params(params)
        except ValueError as e:
            await log(ctx, f"Could not parse params, invalid param format: {e}")
            return
        return await func(ctx, params)
    return inner

def uses_flags(func):
    async def inner(ctx, params: dict[str, str]):
        flags = params.get("flags", None)
        try:
            flags = parse_flags(flags)
        except ValueError as e:
            await log(ctx, f"Could not parse flags, therefore, they won't affect this message. Invalid flags format: {e}")
            return
        return await func(ctx, params, flags)
    return inner


def has_help(message):
    def outer(func):
        async def inner(ctx, params: str | None, flags: Flags):
            if flags is not None and flags['help']:
                await ctx.send(message)
                return
            return await func(ctx, params, flags)
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

async def resend_to(ctx, flags: Flags, thread, message, title: bool = True, delete: bool = True):
    content = message.content
    embeds = message.embeds
    files = [await file.to_file() for file in message.attachments]
    
    if title:
        content = f"-# **{message.author.name}** {message.created_at.strftime(TIME_FORMAT)}:\n\t{content}"
    await thread.send(
        # the first symbol in the string is not a regular space
        content,
        embeds=embeds,
        files=files
    )
    await conditional_log(ctx, flags, f"relocated message {message.id}")
    if delete:
        await message.delete()
        await conditional_log(ctx, flags, f"deleted message {message.id}")

async def resend_messages_to(ctx, flags: Flags, thread, messages, title: bool = True, delete: bool = True):
    for message in messages:
        await resend_to(ctx, flags, thread, message, title, delete)