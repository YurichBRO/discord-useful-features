import re
from parsing import parse_time, parse_flexible_time
from datetime import datetime
from parsing import Flags
from .shared import command, format_limited_len
from log import conditional_log
from json import load, dump

SELECTED_MESSAGES_FILE = 'commands/selected-messages.json'
CONTENT_LOG_LIMIT = 100

def format_content(content: str) -> str: return format_limited_len(content, CONTENT_LOG_LIMIT)

class Selector:
    """Selector for messages"""
    def __init__(self, pattern: str | None = None, ids: set[int] | None = None, start_date: datetime | None = None, end_date: datetime | None = None):
        """Class constructor

        Args:
            pattern (str | None, optional): regex pattern that message content
                is matched to. Defaults to None (any message content is
                accepted).
            ids (set[int] | None, optional): set of ids which the matched
                message has to be in. Defaults to None (any message id is
                accepted).
            start_date (datetime | None, optional): the date, after which the message creation date is required to be. Defaults to None (message after any date is accepted).
            end_date (datetime | None, optional): the date, before which the message creation date is required to be. Defaults to None (message before any date is accepted).
        """
        self.check_query = []
        if pattern:
            self.pattern = re.compile(pattern)
            self.check_query.append(self.check_pattern)
        if ids:
            if not isinstance(ids, set):
                ids = set(ids)
            self.ids = ids
            self.check_query.append(self.check_ids)
        if start_date:
            self.start_date = start_date
            self.check_query.append(self.check_start_date)
        if end_date:
            self.end_date = end_date
            self.check_query.append(self.check_end_date)
    
    def check_pattern(self, message) -> bool:
        return re.search(self.pattern, message.content)
    
    def check_ids(self, message) -> bool:
        return message.id in self.ids
    
    def check_start_date(self, message) -> bool:
        return message.created_at.timestamp() >= self.start_date.timestamp()
    
    def check_end_date(self, message) -> bool:
        return message.created_at.timestamp() <= self.end_date.timestamp()
    
    def match(self, message) -> bool:
        """Check if the message matches the selector

        Args:
            message: discord message object

        Returns:
            bool: True if the message matches the selector, False otherwise
        """
        return all(check(message) for check in self.check_query)


async def get_by_date(ctx, start_date: datetime, end_date: datetime, **kwargs):
    """
    Asynchronously fetch messages within a specified date range from the given context's channel.

    Args:
        ctx: The context object containing information about the invocation.
        start_date (datetime): The start date and time for the message search.
        end_date (datetime): The end date and time for the message search.
        **kwargs: Additional keyword arguments (unused in this function).

    Yields:
        discord.Message: The fetched message objects within the specified date range, one at a time.

    Note:
        This function uses the channel's history method to retrieve messages.
    """
    async for message in ctx.channel.history(after=start_date, before=end_date):
        yield message


async def get_all(ctx, **kwargs):
    """
    Asynchronously fetch all messages from the given context's channel.

    Args:
        ctx: The context object containing information about the invocation.
        **kwargs: Additional keyword arguments (unused in this function).

    Yields:
        discord.Message: All message objects from the channel's history, one at a time.

    Note:
        This function uses the channel's history method to retrieve messages.
    """
    async for message in ctx.channel.history():
        yield message


async def get_by_ids(ctx, ids: list[int], **kwargs):
    """
    Asynchronously fetch messages from the given context's channel using a list of message IDs.

    Args:
        ctx: The context object containing information about the invocation.
        ids (list[int]): A list of message IDs to fetch.

    Yields:
        discord.Message | int: The fetched message objects or the original ID if the message couldn't be fetched.

    Note:
        This function uses the channel's fetch_message method. If a message cannot be fetched
        (e.g., due to permissions or the message not existing), the function yields the original ID.
    """
    for id in ids:
        try:
            yield await ctx.channel.fetch_message(id)
        except:
            yield id


async def get_messages(ctx, flags, pattern: re.Pattern | None, ids: list[int] | None, start_date: datetime | None, end_date: datetime | None):
    if ids:
        selector = Selector(pattern=pattern, start_date=start_date, end_date=end_date)
        generator = get_by_ids
    elif start_date or end_date:
        selector = Selector(pattern=pattern, ids=ids)
        generator = get_by_date
    else:
        selector = Selector(pattern=pattern, ids=ids, start_date=start_date, end_date=end_date)
        generator = get_all
    
    generator = generator(ctx, start_date=start_date, end_date=end_date, ids=ids, pattern=pattern)
    async for message in generator:
        if isinstance(message, int):
            await conditional_log(ctx, flags, f"could not fetch message {message}", important=True)
            continue
        if selector.match(message):
            yield message

"""
modes are:
- add: adds selector
- remove: removes selector
- view: prints out selector from all messages
- filter: prints out selector from already selected messages
"""
data = {
    "name": "select",
    "description": "Selects messages using pattern, ids, and date range (any combination of these can be used)",
    "params": {
        "pattern": {
            "description": "regex pattern that message content is matched to.",
            "required": False,
        },
        "ids": {
            "description": "set of ids which the matched message has to be in.",
            "required": False,
        },
        "start_date": {
            "description": "the date, after which the message creation date is required to be.",
            "required": False,
        },
        "end_date": {
            "description": "the date, before which the message creation date is required to be.",
            "required": False,
        },
        "mode": {
            "description": "the mode to select messages in. 'add' to add to the current selection, 'remove' to remove from the current selection, 'filter' to filter within current selection and print filtered messages, 'view' to filter all threads and print filtered messages, 'clear' to clear the current selection.",
            "required": False,
            "default": "add"
        }
    }
}

@command(data)
async def func(ctx, params: str | None, flags: Flags):
    pattern, ids, start_date, end_date, mode = params

    if pattern:
        pattern = re.compile(pattern)
    if ids:
        ids = list(map(int, ids.split(',')))
    
    if start_date:
        start_date_string = start_date
        try:
            start_date = parse_time(start_date)
            if end_date:
                try:
                    end_date = parse_flexible_time(start_date_string, end_date)
                except:
                    end_date = ""
        except:
            start_date = ""
    else:
        if end_date:
            try:
                end_date = parse_time(end_date)
            except:
                end_date = ""
    
    if mode != "view":
        author = str(ctx.author.id)
        with open(SELECTED_MESSAGES_FILE, 'r') as f:
            selected_messages = load(f)
        if author not in selected_messages:
            selected_messages[author] = []
        await conditional_log(ctx, flags, "Loaded selection")
    if mode in ("add", "remove", "clear"):
        save_selection = True
        count = 0
    else:
        save_selection = False
    if mode == "filter":
        selector = Selector(pattern=pattern, ids=ids, start_date=start_date, end_date=end_date)
        async for message in get_by_ids(ctx, selected_messages[author]):
            if isinstance(message, int):
                continue
            if selector.match(message):
                await ctx.send(f"`{message.id}`\t{format_content(message.content)}")
    elif mode == "view":
        async for message in get_messages(ctx, flags, pattern, ids, start_date, end_date):
            await ctx.send(f"`{message.id}`\t{format_content(message.content)}")
    elif mode == "add":
        async for message in get_messages(ctx, flags, pattern, ids, start_date, end_date):
            if message.id in selected_messages[author]:
                continue
            selected_messages[author].append(message.id)
            count = count + 1
            await conditional_log(ctx, flags, f"selected message {message.id}")
    elif mode == "remove":
        selector = Selector(pattern=pattern, ids=ids, start_date=start_date, end_date=end_date)
        new_selection = selected_messages[author].copy()
        async for message in get_by_ids(ctx, selected_messages[author]):
            if isinstance(message, int):
                new_selection.remove(message)
                count = count - 1
                id = message
                continue
            elif not selector.match(message):
                continue
            new_selection.remove(message.id)
            count = count - 1
            id = message.id
            await conditional_log(ctx, flags, f"removed message {id}")
        selected_messages[author] = new_selection
    elif mode == "clear":
        selected_messages[author] = []
        count = 0
    if save_selection:
        with open(SELECTED_MESSAGES_FILE, 'w') as f:
            dump(selected_messages, f)
        await conditional_log(ctx, flags, f"Selected {count} messages")
    else:
        await conditional_log(ctx, flags, f"Finished logging messages")

name = 'select'
description = 'select messages using pattern, ids, and date range (any combination of these can be used)'