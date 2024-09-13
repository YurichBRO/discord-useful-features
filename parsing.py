from __future__ import annotations
from datetime import datetime

FORMAT = r'%Y-%m-%d-%H:%M:%S'
FORMAT_PARTS = 6

def parse_time(time: str):
    return datetime.strptime(time, FORMAT)

def split_time(time: str):
    return time.replace(':', '-').split('-')

def format_time(parts):
    return f'{parts[0]}-{parts[1]}-{parts[2]}-{parts[3]}:{parts[4]}:{parts[5]}'

def parse_flexible_time(base: str, another: str):
    base_parts = split_time(base)
    another_parts = split_time(another)
    combined = base_parts[:FORMAT_PARTS - len(another_parts)] + another_parts
    return datetime.strptime(format_time(combined), FORMAT)

def parse_params(params: str | None) -> dict[str, str]:
    if not params:
        return {}

    parsed = {}
    key = []
    value = []
    current = key
    escaped = False

    for char in params:
        if escaped:
            current.append(char)
            escaped = False
        elif char == '\\':
            escaped = True
        elif char == '=':
            if not key:
                raise ValueError("Empty parameter name.")
            current = value
        elif char == ';':
            if not key:
                raise ValueError("Empty parameter name.")
            if not value:
                raise ValueError("Empty parameter value.")
            parsed[''.join(key)] = ''.join(value)
            key.clear()
            value.clear()
            current = key
        else:
            current.append(char)

    if key:
        if not value:
            raise ValueError("Empty parameter value.")
        parsed[''.join(key)] = ''.join(value)

    return parsed

def parse_flags(flags: str | None) -> Flags:
    parser = Flags()
    if flags is None:
        return parser
    for flag in parser.FLAGS:
        parser[parser.FLAGS[flag]] = False
    for flag in flags:
        if flag == '-':
            continue
        if flag not in parser.FLAGS:
            raise ValueError(f"Unknown flag: {flag}")
        parser[parser.FLAGS[flag]] = True
    return parser

class Flags:
    FLAGS = {
        'h': 'help',
        'v': 'verbose',
        's': 'silent',
        'r': 'remove-selection'
    }
    
    def __init__(self):
        self.__flags = {self.FLAGS[key]: False for key in self.FLAGS.keys()}
    
    def __getitem__(self, key):
        return self.__flags[key]
    
    def __setitem__(self, key, value):
        self.__flags[key] = value