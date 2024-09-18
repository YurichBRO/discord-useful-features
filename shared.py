from parsing import parse_flags, parse_params, FORMAT as TIME_FORMAT
import discord
from parsing import Flags
from log import conditional_log, log
from json import dump, load


def command(data: dict):
    all_params = data.get("params", {})
    
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
            
            for param_name in all_params:
                if param_name not in params:
                    if all_params[param_name]['required']:
                        await log(ctx, f"Missing required param: {param_name}")
                        return
                    # Assigning default value in case the parameter has a default value
                    default = all_params[param_name].get('default', "")
                    params[param_name] = default
            for param_name in params:
                if param_name not in all_params:
                    await log(ctx, f"Unknown param: {param_name}")
                    return
            
            params = [params[key] for key in all_params]
            
            result = await func(ctx, params, flags)
            return result
        return inner
    return outer


def uses_selection(filepath):
    def outer(func):
        async def inner(ctx, params: list[str], flags: Flags):
            author = str(ctx.author.id)
            with open(filepath, 'r') as f:
                selected_messages = load(f)
                await conditional_log(ctx, flags, "Loaded selection")
            
            if author not in selected_messages:
                selected_messages[author] = []
            
            result = await func(ctx, params, flags, selected_messages[author])
            
            if flags['remove-selection']:
                selected_messages[author] = []
                with open(filepath, 'w') as f:
                    dump(selected_messages, f)
                    await conditional_log(ctx, flags, "Removed selection")
            
            return result
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
        await delete_message(ctx, flags, message)

async def resend_messages_to(ctx, flags: Flags, thread, messages, title: bool = True, delete: bool = True):
    for message in messages:
        await resend_to(ctx, flags, thread, message, title, delete)

async def delete_message(ctx, flags, message):
    await message.delete()
    await conditional_log(ctx, flags, f"deleted message {message.id}")

def format_limited_len(content: str, limit: int = 100) -> str:
    """Formats a string to have limited length
    If string is shorter that limit, it doesn't change.
    Otherwise, it truncates the string and adds `...` at the end.

    Args:
        content (str): the string that is being formatted
        limit (int, optional): the maximum length of the string (including `...`). Defaults to 100.

    Returns:
        str: formatted string
    """
    if len(content) > limit:
        return content[:limit-3] + "..."
    return content