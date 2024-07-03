from enum import Enum
import re

class CommandType(Enum):
    A_COMMAND = 1
    C_COMMAND = 2
    L_COMMAND = 3

class Parse:
    def __init__(self, file_path):
        try:
            with open(file_path) as f:
                self.input_file = f.read().split('\n')
        except FileNotFoundError:
            print("file not found!")
            exit(1)
        self.current = 0
        self._dest = None
        self._comp = None
        self._jmp = None
        self._symbol = None

    @property
    def dest(self):
        return self._dest
        
    @property
    def comp(self):
        return self._comp

    @property
    def jmp(self):
        return self._jmp
    
    @property
    def symbol(self):
        return self._symbol
    
    def has_more_commands(self):
        
        if self.current < len(self.input_file):
            return True
        return False
    
    def advance(self):
        if self.has_more_commands():
            self.current += 1

    def command_type(self):
        line = self.input_file[self.current].split('//')[0].strip()
        pattern = r'([MDA]+)?=?([^;]+)(?:;(.+)?)?'

        if line.startswith('@'):
            self._symbol = line[1:].strip()
            return CommandType.A_COMMAND
        elif line.startswith('('):
            self._symbol = line[1:-1].strip()
            return CommandType.L_COMMAND
        elif found := re.search(pattern, line):
            dest, comp, jmp = found.groups()
            self._dest = dest if dest else ""
            self._comp = comp if comp else ""
            self._jmp = jmp if jmp else ""

            return CommandType.C_COMMAND
            
        return None
