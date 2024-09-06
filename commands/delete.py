from time_parsing import parse_time
from flags import parse
from log import conditional_log, flags_missing

async def delete(ctx,
                 flags: str | None,
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
        await conditional_log(ctx, flags, "Usage: `/delete -[flags] [start_date] [end_date]`", important=True)
        return
    if start_date is None or end_date is None:
        await conditional_log(ctx, flags, "Please provide both start and end dates.", important=True)
        return
    # Convert date strings to datetime objects
    try:
        start_datetime = parse_time(start_date)
        end_datetime = parse_time(end_date)
    except ValueError:
        await conditional_log(ctx, flags, "Invalid date format.", important=True)
        return
    
    # Fetch messages from the channel
    messages = [message async for message in ctx.channel.history(limit=None, after=start_datetime, before=end_datetime)]
    await conditional_log(ctx, flags, f"Fetched {len(messages)} messages from {start_date} to {end_date}.")
    
    # Delete messages
    for message in messages:
        await message.delete()
        await conditional_log(ctx, flags, f"deleted message {message.id}")
    
    await conditional_log(ctx, flags, f"Messages from {start_date} to {end_date} have been deleted.")