"""
this is a placeholder file to /help command
it's defined in main.py because of implementation details, but for the sake of
consistency, its data is described here, it's there for users to be able to do
`/help help`
"""

data = {
    "name": "help",
    "description": "Get help on a specific command",
    "uses-decorator": False
}

async def func(ctx, command_name: str | None):
    """this function is redefined in main.py, this is once again a placeholder"""