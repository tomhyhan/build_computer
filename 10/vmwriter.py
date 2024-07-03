class VMwriter:
    def __init__(self, file_name, mode):
        self.filename = file_name
        self.mode = mode
    
    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self
    
    def __exit__(self, *args, **kargs):
        if self.file:
            self.file.close() 
    
    def write_push(self, segment, idx):
        if segment == "var":
            segment = "local"
        elif segment == "arg":
            segment = "argument"
        elif segment == "field":
            segment = "this"
        
        self.write(f"push {segment} {idx}")
    
    def write_pop(self, segment, idx):
        if segment == "var":
            segment = "local"
        elif segment == "arg":
            segment = "argument"
        elif segment == "field":
            segment = "this"
            
        self.write(f"pop {segment} {idx}")
    
    def write_arithmetic(self, command):
        self.write(command)
    
    def write_label(self, label):
        self.write(f"label {label}")
    
    def write_goto(self, label):
        self.write(f"goto {label}")
    
    def write_if(self, label):
        self.write(f"if-goto {label}")
    
    def write_call(self, name, nargs):
        return self.write(f"call {name} {nargs}")
    
    def write_function(self, name, nlocals):
        self.write(f"function {name} {nlocals}")
    
    def write_return(self):
        self.write("return")
    
    def write(self, content):
        self.file.write(content + "\n")
    
    def close(self):
        pass