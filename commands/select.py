import re
from parsing import parse_time, parse_flexible_time
from datetime import datetime
from parsing import Flags, FORMAT as TIME_FORMAT
from .shared import command
from log import conditional_log
from json import load, dump

SELECTED_MESSAGES_FILE = 'commands/selected-messages.json'
CONTENT_LOG_LIMIT = 100

def format_content(content: str) -> str:
    if len(content) > CONTENT_LOG_LIMIT:
        return content[:CONTENT_LOG_LIMIT] + "..."
    return content

class Selector:
    def __init__(self, pattern: str | None = None, ids: set[int] | None = None, start_date: datetime | None = None, end_date: datetime | None = None):
        self.check_query = []
        if pattern:
            self.pattern = re.compile(pattern)
            self.check_query.append(self.check_pattern)
        if ids:
            self.ids = ids
            self.check_query.append(self.check_ids)
        if start_date:
            self.start_date = start_date
            self.check_query.append(self.check_start_date)
        if end_date:
            self.end_date = end_date
            self.check_query.append(self.check_end_date)
    
    def check_pattern(self, message) -> bool:
        return re.match(self.pattern, message.content)
    
    def check_ids(self, message) -> bool:
        return message.id in self.ids
    
    def check_start_date(self, message) -> bool:
        return message.created_at.timestamp() >= self.start_date.timestamp()
    
    def check_end_date(self, message) -> bool:
        return message.created_at.timestamp() <= self.end_date.timestamp()
    
    def match(self, message) -> bool:
        return all(check(message) for check in self.check_query)


async def get_by_ids(ctx, ids: set[int], **kwargs):
    for message_id in ids:
        yield await ctx.channel.fetch_message(message_id)


async def get_by_date(ctx, start_date: datetime, end_date: datetime, **kwargs):
    async for message in ctx.channel.history(after=start_date, before=end_date):
        yield message


async def get_all(ctx, **kwargs):
    async for message in ctx.channel.history():
        yield message


async def get_messages_from_ids(ctx, ids: list[int]):
    for id in ids:
        try:
            yield await ctx.channel.fetch_message(id)
        except:
            yield id


async def get_messages(ctx, pattern: re.Pattern | None, ids: list[int] | None, start_date: datetime | None, end_date: datetime | None):
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
        if selector.match(message):
            yield message

"""
modes are:
- add: adds selector
- remove: removes selector
- view: prints out selector from all messages
- filter: prints out selector from already selected messages
"""
@command(
    {
        "pattern": "",
        "ids": "",
        "start_date": "",
        "end_date": "",
        "mode": "add",
    },
    "Usage: select [pattern] [ids] [start_date] [end_date] [remove]",
)
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
    if mode in ("add", "remove"):
        save_selection = True
        count = 0
    else:
        save_selection = False
    if mode == "filter":
        selector = Selector(pattern=pattern, ids=ids, start_date=start_date, end_date=end_date)
        async for message in get_messages_from_ids(ctx, selected_messages[author]):
            if isinstance(message, int):
                continue
            if selector.match(message):
                await ctx.send(f"`{message.id}`\t{format_content(message.content)}")
    elif mode == "view":
        async for message in get_messages(ctx, pattern, ids, start_date, end_date):
            await ctx.send(f"`{message.id}`\t{format_content(message.content)}")
    elif mode == "add":
        async for message in get_messages(ctx, pattern, ids, start_date, end_date):
            if message.id in selected_messages[author]:
                continue
            selected_messages[author].append(message.id)
            count = count + 1
            await conditional_log(ctx, flags, f"selected message {message.id}")
    elif mode == "remove":
        selector = Selector(pattern=pattern, ids=ids, start_date=start_date, end_date=end_date)
        new_selection = selected_messages[author].copy()
        async for message in get_messages_from_ids(ctx, selected_messages[author]):
            if not selector.match(message):
                continue
            if isinstance(message, int):
                new_selection.remove(message)
                count = count - 1
                id = message
            elif message.id in selected_messages[author]:
                new_selection.remove(message.id)
                count = count - 1
                id = message.id
            else:
                continue
            await conditional_log(ctx, flags, f"removed message {id}")
        selected_messages[author] = new_selection
    if save_selection:
        with open(SELECTED_MESSAGES_FILE, 'w') as f:
            dump(selected_messages, f)
        await conditional_log(ctx, flags, f"Selected {count} messages")
    else:
        await conditional_log(ctx, flags, f"Finished logging messages")

name = 'select'
description = 'select messages using pattern, ids, and date range (any combination of these can be used)'