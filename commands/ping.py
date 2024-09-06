from flags import parse
from log import conditional_log, flags_missing

async def ping(ctx, flags: str | None):
    if flags == None:
        await flags_missing(ctx)
        return
    try:
        flags = await parse(ctx, flags)
    except ValueError:
        return
    if flags['help']:
        await conditional_log(ctx, flags, "Usage: /ping [flags]", important=True)
        return
    await conditional_log(ctx, flags, 'pong', important=True)
    await conditional_log(ctx, flags, 'verbose pong')