from flags import Flags

async def conditional_log(ctx, flags: Flags, message: str, important: bool = False):
    if flags['silent']: return
    if not important and not flags['verbose']: return
    await log(ctx, message)

async def log(ctx, message: str):
    await ctx.send(message)

async def flags_missing(ctx):
    await ctx.send("Flags parameter is required. If you don't want to use flags, use the `-` symbol as a placeholder.")