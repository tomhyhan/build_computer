from tokenizer import Tokenizer
from symtab import Symtab
from vmwriter import VMwriter
class CompilationEngine:
    def __init__(self, filename, tokenizer : Tokenizer, symtab: Symtab, vm_writer: VMwriter, mode="w",):
        self.filename = filename
        self.mode = mode
        self.tokenizer = tokenizer
        self.tab = 0
        self.symtab = symtab
        self.vm_writer = vm_writer
        self.ops = ['+','-','*','/','&','|','<','>','=']
        self.unaryops = ['-', '~']
        self.class_name = None
        self.ops_to_vm = {
            '+': "add",
            '-': "sub",
            '*': "call Math.multiply 2",
            '/': "call Math.divide 2",
            '&': "and",
            '|': "or",
            '<': "lt",
            '>': "gt",
            '=': "eq"
        }
        self.if_cnt = 0
        self.while_cnt = 0
        
    def compile_class(self):
        self.xml("<class>")
        self.tab += 2

        self.compile_keyword()
        
        self.class_name = self.compile_identifier()

        self.compile_symbol()
    
        # self.compile_class_var_dec()
        
        while self.tokenizer.token in ["static", "field"]:
            self.compile_class_var_dec()
        
        while self.tokenizer.token in ["constructor", "function", "method"]:
            self.compile_subroutine()

        self.compile_symbol(False)
        
        self.tab -= 2
        self.xml("</class>")
    
    def compile_keyword(self):
        assert(self.tokenizer.token_type() == "keyword")
        token = self.tokenizer.token
        self.xml(f"<{self.tokenizer.token_type()}> {token} </{self.tokenizer.token_type()}>")
        self.tokenizer.advance()
        
        return token

    def compile_identifier(self):
        assert(self.tokenizer.token_type() == "identifier")
        
        token = self.tokenizer.token

        self.xml(f"<{self.tokenizer.token_type()}> {token} </{self.tokenizer.token_type()}>")
        self.tokenizer.advance()
        
        return token
        
    def compile_symbol(self, do_advance=True):
        assert(self.tokenizer.token_type() == "symbol")
        token = self.tokenizer.token 
        self.xml(f"<{self.tokenizer.token_type()}> {token} </{self.tokenizer.token_type()}>")
        
        if do_advance:
            self.tokenizer.advance()
            
        return token
    
    def complile_int(self):
        assert(self.tokenizer.token_type() == "integerConstant")
        
        token = self.tokenizer.token 
        self.xml(f"<{self.tokenizer.token_type()}> {token} </{self.tokenizer.token_type()}>")
        self.tokenizer.advance()
        
        return token
    
    def complile_string(self):
        assert(self.tokenizer.token_type() == "stringConstant")
        
        token = self.tokenizer.token
        self.xml(f"<{self.tokenizer.token_type()}> {self.tokenizer.token} </{self.tokenizer.token_type()}>")
        self.tokenizer.advance()
        
        return token
        
    def compile_class_var_dec(self):
        self.xml("<classVarDec>")
        self.tab +=2
        
        kind = self.compile_keyword()
        type, name = self.type_varname()
        print(name, type, kind)
        self.symtab.define(name, type, kind, self.xml)
        
        # possible refactor 2
        while  self.tokenizer.token == ',':
            self.compile_symbol()
            name = self.compile_identifier()
            self.symtab.define(name, type, kind, self.xml)

        self.compile_symbol()
        
        self.tab -= 2
        self.xml("</classVarDec>")
    
    def compile_subroutine(self):
        self.xml("<subroutineDec>")
        self.tab += 2
        self.symtab.start_subroutine()
        
        subroutine_name = self.compile_keyword()
        
        type, name = self.type_varname()

        # only add this when function is method
        if subroutine_name == "method":
            self.symtab.define("this", type, "arg", self.xml)
        
        self.compile_symbol()
        self.compile_parameterlist()            
        self.compile_symbol()
        
        # print(subroutine_name, type, name, self.symtab.sub_symtab)
        self.compile_subroutine_body(name, subroutine_name)
        
        self.tab -= 2
        self.xml("</subroutineDec>")
    
    def compile_subroutine_body(self, name, subroutine_name):
        self.xml("<subroutineBody>")
        self.tab += 2
        
        # '{' 
        self.compile_symbol()
        
        # vardec
        while self.tokenizer.token == "var":
            self.compile_var_dec()
            
        nlocals = self.symtab.var_count("var")
        self.vm_writer.write_function(f"{self.class_name}.{name}", nlocals)
        
        if subroutine_name == "constructor":
            nfield = self.symtab.var_count("field")
            self.vm_writer.write_push("constant", nfield)
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("pointer", 0)
        elif subroutine_name == "method":
            self.vm_writer.write_push("argument", 0)
            self.vm_writer.write_pop("pointer", 0)
            
        # statements
        self.compile_statements()
        
        # '}'
        self.compile_symbol()
        
        self.tab -= 2
        self.xml("</subroutineBody>")
    
    
    def compile_parameterlist(self):
        self.xml("<parameterList>")
        self.tab +=2
        
        if self.tokenizer.token != ')':
            type, name = self.type_varname()
            self.symtab.define(name, type, "arg", self.xml)
            while self.tokenizer.token == ",":
                self.compile_symbol()
                type, name = self.type_varname()
                self.symtab.define(name, type, "arg", self.xml)
                print(type,name)
        
        self.tab -= 2
        self.xml("</parameterList>")

    def compile_var_dec(self):
        self.xml("<varDec>")
        self.tab +=2
        
        # varDec*
        kind = self.compile_keyword()
        type, name = self.type_varname()
        self.symtab.define(name, type, kind, self.xml)
        while self.tokenizer.token == ',':
            self.compile_symbol()
            name = self.compile_identifier()
            self.symtab.define(name, type, kind, self.xml)
        
        self.compile_symbol()
        
        self.tab -= 2
        self.xml("</varDec>")
    
    def compile_statements(self):
        self.xml("<statements>")
        self.tab +=2
        
        while self.tokenizer.token in ["let", "if", "while", "do", "return"]:
            match self.tokenizer.token:
                case "let":
                    self.compile_let()
                case "if":
                    self.compile_if()
                case "while":
                    self.compile_while()
                case "do":
                    self.compile_do()
                case "return":
                    self.compile_return()

        self.tab -=2
        self.xml("</statements>")
        
    
    def compile_do(self):
        self.xml("<doStatement>")
        self.tab +=2

        self.compile_keyword()
        obj = self.compile_identifier()
        self.compile_subroutine_call(obj)
        self.compile_symbol()

        # for do, there no variable to save the result
        self.vm_writer.write_pop("temp", 0)
        
        self.tab -=2
        self.xml("</doStatement>")  
    
    def compile_let(self):
        self.xml("<letStatement>")
        self.tab +=2

        # let varName
        self.compile_keyword()
        save_to = self.compile_identifier()
        
        # let depends on whether a variable is scalar or object 
        is_Array = False
        
        #  ('[' expression ']')?
        while self.tokenizer.token == '[':
            is_Array = True
            self.compile_symbol()
            self.compile_expression()
            self.compile_symbol()
            
            idx = self.symtab.indexof(save_to)
            segment = self.symtab.kindof(save_to)
            self.vm_writer.write_push(segment, idx)
            
            self.vm_writer.write_arithmetic("add")
            
        # =
        self.compile_symbol()
        # expression
        self.compile_expression()
        # ;
        self.compile_symbol()
            
        if is_Array:
            self.vm_writer.write_pop("temp", 0)
            self.vm_writer.write_pop("pointer", 1)
            self.vm_writer.write_push("temp", 0)
            self.vm_writer.write_pop("that", 0)
        else:
            idx = self.symtab.indexof(save_to)
            segment = self.symtab.kindof(save_to)
            self.vm_writer.write_pop(segment, idx)

        self.tab -= 2
        self.xml("</letStatement>")
    
    def compile_while(self):
        self.xml("<whileStatement>")
        self.tab +=2

        # while
        self.compile_keyword()
        
        # '(' expression ')' '{' statements '}'
        false_label = f"WHILE_FALSE{self.while_cnt}"
        true_label = f"WHILE_TRUE{self.while_cnt}"
        self.while_cnt += 1
        
        self.vm_writer.write_label(true_label)
        self.compile_symbol()
        self.compile_expression()
        self.compile_symbol()
        
        self.vm_writer.write_arithmetic("not")
        
        self.vm_writer.write_if(false_label)
        self.compile_symbol()
        self.compile_statements()
        self.compile_symbol()
        self.vm_writer.write_goto(true_label)
        
        self.vm_writer.write_label(false_label)
        
        self.tab -=2
        self.xml("</whileStatement>")    
    
    def compile_return(self):
        self.xml("<returnStatement>")
        self.tab +=2
        
        self.compile_keyword()
        
        void = True
        if self.tokenizer.token != ';':
            self.compile_expression()
            void = False
            
        self.compile_symbol()
        
        if void:
            self.vm_writer.write_push("constant", 0)
            
        self.vm_writer.write_return()
        
        self.tab -=2
        self.xml("</returnStatement>")
    
    def compile_if(self):
        self.xml("<ifStatement>")
        self.tab +=2
        
        self.compile_keyword()
        self.compile_symbol()
        self.compile_expression()
        
        self.vm_writer.write_arithmetic("not")
        false_label = f"IF_FALSE{self.if_cnt}"
        true_label = f"IF_TRUE{self.if_cnt}"
        self.if_cnt += 1
        
        self.vm_writer.write_if(false_label)
        self.compile_symbol()
        self.compile_symbol()
        self.compile_statements()
        self.compile_symbol()
        self.vm_writer.write_goto(true_label)
        
        # else?
        self.vm_writer.write_label(false_label)
        if self.tokenizer.token == "else":
            self.compile_keyword()
            self.compile_symbol()
            self.compile_statements()
            self.compile_symbol()

        self.vm_writer.write_label(true_label)
        self.tab -=2
        self.xml("</ifStatement>")

    def compile_expression(self):
        self.xml("<expression>")
        self.tab +=2
        
        self.compile_term()
        
        while self.tokenizer.token in self.ops:
            op = self.compile_symbol()
            self.compile_term()
            self.vm_writer.write_arithmetic(self.ops_to_vm[op])
        self.tab -= 2
        self.xml("</expression>")
    
    def compile_term(self):
        self.xml("<term>")
        self.tab += 2
        
        ctoken = self.tokenizer.token
        ctype = self.tokenizer.token_type()

        if ctype == "integerConstant":
            integer = self.complile_int()
            self.vm_writer.write_push("constant", integer)
        elif ctype == "stringConstant":
            string = self.complile_string()
            n_string = len(string)
            self.vm_writer.write_push("constant", n_string)
            self.vm_writer.write_call("String.new", 1)
            for char in string:
                self.vm_writer.write_push("constant", ord(char))
                self.vm_writer.write_call("String.appendChar", 2)
        elif ctoken in ["true", "false", "null", "this"]:
            if ctoken == "this":
                self.vm_writer.write_push("pointer", 0)
            elif ctoken == "true":
                self.vm_writer.write_push("constant", 1)
                self.vm_writer.write_arithmetic("neg")
            elif ctoken in ["false", "null"]:
                self.vm_writer.write_push("constant", 0)
            self.compile_keyword()
        elif ctype == "identifier":
            obj = self.compile_identifier()
            is_array = False
            if self.tokenizer.token == '[':
                self.compile_symbol()
                self.compile_expression()
                self.compile_symbol()
                idx = self.symtab.indexof(obj)
                segment = self.symtab.kindof(obj)
                self.vm_writer.write_push(segment, idx)
                self.vm_writer.write_arithmetic("add")
                is_array = True
            call_subroutine = self.compile_subroutine_call(obj)
            if is_array:
                self.vm_writer.write_pop("pointer", 1)
                self.vm_writer.write_push("that", 0)
            elif not call_subroutine:
                idx = self.symtab.indexof(obj)
                segment = self.symtab.kindof(obj)
                self.vm_writer.write_push(segment, idx)
        elif ctoken == '(':
            self.compile_symbol()
            self.compile_expression()
            self.compile_symbol()
        elif ctoken in self.unaryops:
            uop = "neg" if ctoken == '-' else "not"
            self.compile_symbol()
            self.compile_term()
            self.vm_writer.write_arithmetic(uop)
        else:
            raise Exception("wrong grammer")
        
        self.tab -= 2
        self.xml("</term>")
    
    def compile_expressionlist(self):
        self.xml("<expressionList>")
        self.tab +=2
        
        n_args = 0
        if self.tokenizer.token != ')':
            self.compile_expression()
            n_args += 1
            while self.tokenizer.token == ',':
                self.compile_symbol()
                self.compile_expression()
                n_args += 1
        self.tab -=2
        self.xml("</expressionList>")
    
        return n_args
    
    def compile_subroutine_call(self, obj=None):
        ctoken = self.tokenizer.token
        call_subroutine = False
        if ctoken == '(':
            call_subroutine = True
            self.vm_writer.write_push('pointer', 0)
            self.compile_symbol()
            n_args = self.compile_expressionlist()
            self.compile_symbol()
            self.vm_writer.write_call(f'{self.class_name}.{obj}', n_args+1)
        elif ctoken == '.':
            call_subroutine = True
            # class.method
            # if method is in symtab push the object
            # Otherwise if method is new do nothing
            self.compile_symbol()
            method = self.compile_identifier()
            self.compile_symbol()
            
            if obj in self.symtab.sub_symtab or obj in self.symtab.class_symtab:
                self.vm_writer.write_push(self.symtab.kindof(obj), self.symtab.indexof(obj))
            
            n_args = self.compile_expressionlist()
            
            # here!
            # print("method", method)
            # print(self.symtab.sub_symtab, self.symtab.class_symtab, obj)
            if obj in self.symtab.sub_symtab or obj in self.symtab.class_symtab:
                # print("obj", obj)
                # print("self.symtab.kindof(obj)", self.symtab.kindof(obj))
                self.vm_writer.write_call(f"{self.symtab.typeof(obj)}.{method}",n_args + 1)
            else:
                self.vm_writer.write_call(f"{obj}.{method}", n_args)
            
            
            self.compile_symbol()
        return call_subroutine
    
    # utility functions
    def type_varname(self):
        if self.tokenizer.token_type() == "keyword":
            type = self.compile_keyword()
        else:
            type = self.compile_identifier()
        name = self.compile_identifier()
        return type, name
    
    def more_varname(self):
        while self.tokenizer.token == ',':
            self.compile_symbol()
            self.compile_identifier()

    def xml(self, content):
        self.file.write(f"{' ' * self.tab}{content}\n")

    def token(self):
        print("current token: ", self.tokenizer.token)

    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self
    
    def __exit__(self, *args, **kargs):
        if self.file:
            self.file.close() 
            
