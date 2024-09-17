name = 'select_threads'
description = 'select threads using pattern, ids, and date range (any combination of these can be used)'

import re
from datetime import datetime
from .shared import command, format_limited_len
from log import conditional_log
from parsing import parse_time, parse_flexible_time
from json import load, dump
from parsing import Flags

SELECTED_THREADS_FILE = 'commands/selected-threads.json'
NAME_LOG_LIMIT = 100

def format_name(content: str) -> str: return format_limited_len(content, NAME_LOG_LIMIT)

class Selector:
    """Selector for threads"""
    def __init__(self, pattern: str | None = None, ids: set[int] | None = None, start_date: datetime | None = None, end_date: datetime | None = None):
        """Class constructor
        
        Args:
            pattern (str | None, optional): regex pattern that thread name
                is matched to. Defaults to None (any thread name is accepted)
            ids (set[int] | None, optional): set of ids which the matched
                thread has to be in. Defaults to None (any thread id is accepted).
            start_date (datetime | None, optional): the date, after which the
                thread creation date is required to be. Defaults to None
                (thread after any date is accepted).
            end_date (datetime | None, optional): the date, before which the
                thread creation date is required to be. Defaults to None
                (thread before any date is accepted).
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
    
    def check_pattern(self, thread) -> bool:
        return re.search(self.pattern, thread.name)
    
    def check_ids(self, thread) -> bool:
        return thread.id in self.ids
    
    def check_start_date(self, thread) -> bool:
        return thread.created_at.timestamp() >= self.start_date.timestamp()
    
    def check_end_date(self, thread) -> bool:
        return thread.created_at.timestamp() <= self.end_date.timestamp()
    
    def match(self, thread) -> bool:
        """Check if the thread matches the selector
        
        Args:
            thread (discord.Thread): the thread to check
            
        Returns:
            bool: whether the thread matches the selector
        """
        return all(check(thread) for check in self.check_query)


def get_threads(ctx, flags, pattern: re.Pattern | None = None, ids: set[int] | None = None, start_date: datetime | None = None, end_date: datetime | None = None):
    selector = Selector(pattern, ids, start_date, end_date)
    for thread in ctx.channel.threads:
        if selector.match(thread):
            yield thread


def get_by_ids(ctx, ids: set[int]):
    threads = {thread.id: thread for thread in ctx.channel.threads}
    for i in ids:
        yield threads.get(i, i)


@command(
    {
        "pattern": "",
        "ids": "",
        "start_date": "",
        "end_date": "",
        "mode": "add",
    },
    "Usage: `/select_threads [pattern] [ids] [start_date] [end_date] [mode]`\n"
)
async def func(ctx, params: str | None, flags: Flags):
    pattern, ids, start_date, end_date, mode = params
    
    if pattern:
        pattern = re.compile(pattern)
    if ids:
        ids = set(map(int, ids.split(',')))
    
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
            end_date_string = end_date
            try:
                end_date = parse_flexible_time(end_date_string)
            except:
                end_date = ""
    
    if mode != "view":
        author = str(ctx.author.id)
        with open(SELECTED_THREADS_FILE, 'r') as f:
            selected_threads = load(f)
        if author not in selected_threads:
            selected_threads[author] = []
        await conditional_log(ctx, flags, "Loaded selection")
    if mode in ("add", "remove"):
        save_selection = True
        count = 0
    else:
        save_selection = False
    if mode == "filter":
        selector = Selector(pattern=pattern, ids=ids, start_date=start_date, end_date=end_date)
        for thread in get_by_ids(ctx, selected_threads[author]):
            if isinstance(thread, int):
                continue
            if selector.match(thread):
                await ctx.send(f"`{thread.id}`\t{format_name(thread.name)}")
    elif mode == "view":
        for thread in get_threads(ctx, flags, pattern, ids, start_date, end_date):
            await ctx.send(f"`{thread.id}`\t{format_name(thread.name)}")
    elif mode == "add":
        for thread in get_threads(ctx, flags, pattern, ids, start_date, end_date):
            if thread.id in selected_threads[author]:
                continue
            selected_threads[author].append(thread.id)
            count += 1
            await conditional_log(ctx, flags, f"selected thread {thread.id}")
    elif mode == "remove":
        selector = Selector(pattern=pattern, ids=ids, start_date=start_date, end_date=end_date)
        new_selected_threads = selected_threads[author].copy()
        for thread in get_by_ids(ctx, selected_threads[author]):
            if isinstance(thread, int):
                continue
            if not selector.match(thread):
                continue
            new_selected_threads.remove(thread.id)
            count += 1
            await conditional_log(ctx, flags, f"removed thread {thread.id}")
        selected_threads[author] = new_selected_threads
    if save_selection:
        with open(SELECTED_THREADS_FILE, 'w') as f:
            dump(selected_threads, f)
        await conditional_log(ctx, flags, f"Selected {count} threads")
    else:
        await conditional_log(ctx, flags, f"Finished logging threads")