from __future__ import annotations
from datetime import datetime

FORMATS = [
    '%Y-%m-%d-%H:%M:%S',
]

def parse_time(time_str: str) -> datetime:
    for format in FORMATS:
        try:
            return datetime.strptime(time_str, format)
        except ValueError:
            pass
    raise ValueError("Invalid time format")

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
        elif char == ',':
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
    if flags[0] != '-':
        raise ValueError("Flags must start with a `-`")
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
        'd': 'delete',
        'v': 'verbose',
        's': 'silent',
    }
    
    def __init__(self):
        self.__flags = {self.FLAGS[key]: False for key in self.FLAGS.keys()}
    
    def __getitem__(self, key):
        return self.__flags[key]
    
    def __setitem__(self, key, value):
        self.__flags[key] = value