def parse(flags: str):
    parser = Flags()
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
        self.__flags = {}
    
    def __getitem__(self, key):
        return self.__flags[key]
    
    def __setitem__(self, key, value):
        self.__flags[key] = value