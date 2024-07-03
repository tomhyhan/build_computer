import re 

COMMENT = r"(\/\/.*)|(\/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+\/)"
KEYWORD = r"^\s*(class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return)\b\s*"
SYMBOL = r"^\s*({|}|\(|\)|\[|\]|\.|\,|\||;|\+|-|\*|\/|&|<|>|=|~)\s*"
INT_CONST = r"^\s*(\d+)\s*"
STRING_CONST = r"^\s*\"(.*)\"\s*"
IDENTIFIER = r"^\s*([a-zA-Z_][a-zA-Z1-9_]*)\s*"

class Tokenizer:
    KEYWORD = 0
    SYMBOL = 1
    IDENTIFIER = 2
    INT_CONST = 3
    STRING_CONST = 4
    
    def __init__(self, input_file):
        self.symbols = {}
        self.token = None
        self.token_T = None
        
        with open(input_file) as f:
            self.file = f.read()
            self.remove_comments()

        self.advance()
        
    def remove_comments(self):
        self.file = re.sub(COMMENT,"",  self.file)

    def has_more_tokens(self):
        if not self.file:
            return False
        return True
    
    def can_search_and_replace(self, pattern, token_type):
        search = re.search(pattern, self.file)
        if search:
            self.token = search.groups()[0]
            # print("token:", self.token)
            self.token_T = token_type
            self.file = re.sub(pattern, "", self.file, 1)
            return True
        return False
    
    def advance(self):
        patterns = [(KEYWORD, Tokenizer.KEYWORD),
                    (SYMBOL, Tokenizer.SYMBOL),
                    (INT_CONST, Tokenizer.INT_CONST),
                    (STRING_CONST, Tokenizer.STRING_CONST),
                    (IDENTIFIER, Tokenizer.IDENTIFIER)]
        
        for pattern, token_type in patterns:
            if self.can_search_and_replace(pattern, token_type):
                return 
        # print(self.file)
        raise Exception("should not reach here!")
        
    
    def token_type(self):
        match self.token_T:
            case Tokenizer.KEYWORD:
                return "keyword"
            case Tokenizer.SYMBOL:
                return "symbol"
            case Tokenizer.STRING_CONST:
                return "stringConstant"
            case Tokenizer.INT_CONST:
                return "integerConstant"
            case Tokenizer.IDENTIFIER:
                return "identifier"
    
    def keyword(self):
        return self.token
    
    def symbol(self):
        return self.token
    
    def identifier(self):
        return self.token
    
    def int_val(self):
        return self.token
    
    def string_val(self):
        return self.token