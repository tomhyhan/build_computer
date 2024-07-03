class Parser:
    C_ARITHMETIC=0
    C_PUSH=1, 
    C_POP=2,
    C_LABEL=3,
    C_GOTO=4, 
    C_IF=5,
    C_FUNCTION=6,
    C_RETURN=7,
    C_CALL=8,
    
    def __init__(self, filepath):
        with open(filepath) as f:
            self.file = [line for line in f.read().split('\n') if line.split('//')[0] != '']
        self.seek = 0

    def has_more_commands(self):
        if self.seek >= len(self.file):
            return False
        return True
    
    def advance(self):
        self.seek += 1

    @property
    def current_instruction(self):
        return self.file[self.seek]

    def get_tokens(self):
        return self.current_instruction.split()

    def commandType(self):
        tokens = self.get_tokens()
        match tokens[0]:
            case "push":
                return Parser.C_PUSH
            case "pop":
                return Parser.C_POP
            case "label":
                return Parser.C_LABEL
            case "function":
                return Parser.C_FUNCTION
            case "if-goto":
                return Parser.C_IF
            case "goto":
                return Parser.C_GOTO
            case "return":
                return Parser.C_RETURN
            case "call":
                return Parser.C_CALL
            case _:
                return Parser.C_ARITHMETIC

    @property
    def arg1(self):
        tokens = self.get_tokens()

        assert(self.commandType() != Parser.C_RETURN)
        
        if self.commandType() == Parser.C_ARITHMETIC:
            return tokens[0]
        return tokens[1]
        
    @property
    def arg2(self):
        tokens = self.get_tokens()
        
        assert(self.commandType() in [Parser.C_PUSH, Parser.C_POP, Parser.C_FUNCTION, Parser.C_CALL])

        return tokens[2]