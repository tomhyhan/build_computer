import os

class CodeWriter:
    def __init__(self, filename, mode='a', debug=True):
        self.filename = filename
        self.mode = mode 
        self.line_num = 0  
        self.debug = debug
        self.n_cmp_fn = 0
        self.n_return = 0
        self.cmp_command = {
            "eq" : "JEQ",
            "lt": "JLT",
            "gt": "JGT",
        }
        self.mem_map = {
            "argument": "ARG",
            "local": "LCL",
            "that": "THAT",
            "this": "THIS",
            "temp": 5,
            "pointer": 3,
            "static": 16,
            "general": 15
        }
        
    def set_filename(self, vm_path):
        self.vm_filename = os.path.splitext(os.path.basename(vm_path))[0]
        
    def write(self, content):
        self.file.write(f"{content}")
        if self.debug:
            self.file.write(f" // {self.line_num}")
            self.line_num += 1
        self.file.write(f"\n")
    
    def write_arithmetic(self, command):

        if command not in ["neg", "not"]:
            # get prev sp value save to D
            self.decrease_sp()
            self.save_current_stack_value_to_D()

        # decrease sp
        self.decrease_sp()
                
        # point to current stack value
        self.write("@SP")
        self.write("A=M")
        
        match command:
            case "add":
                self.write("M=M+D")
            case "sub":
                self.write("M=M-D")
            case "neg":
                self.write("M=-M")
            case "and":
                self.write("M=M&D")
            case "or":
                self.write("M=M|D")
            case "not":
                self.write("M=!M")
            case "eq" | "lt" | "gt":
                # compare and jump condition
                self.write("D=M-D")
                
                self.write(f"@CMP_TRUE_{self.n_cmp_fn}")
                self.write(f"D;{self.cmp_command[command]}")
                
                # condition fail
                self.write("@SP")
                self.write("A=M")
                self.write("M=0")
                self.write(f"@CMP_END_{self.n_cmp_fn}")
                self.write(f"0;JMP")
                
                # condition true
                self.write(f"(CMP_TRUE_{self.n_cmp_fn})")
                self.write("@SP")
                self.write("A=M")
                self.write("M=-1")
                
                # END
                self.write(f"(CMP_END_{self.n_cmp_fn})")
                
                self.n_cmp_fn += 1
        self.increase_sp()
        
    def write_push_pop(self, command, segment, index=0):
        # argument, local, static, constant,
        # this, that, pointer,
        # temp
        match command:
            case "push":
                if segment == "constant":
                    # get constant value
                    self.write(f"@{index}")
                    self.write("D=A")
                    
                    self.save_and_inc_stack()
                else:
                    self.point_segment_addr(segment, index)

                    # get value of segment
                    self.write("D=M")

                    self.save_and_inc_stack()
            case "pop":
                assert(segment != "constant")
                general_reg = self.mem_map["general"]
                
                
                # save segment[index] address to general reg
                self.point_segment_addr(segment, index) 
                self.write("D=A")
                self.write(f"@R{general_reg}")
                self.write(f"M=D")
                
                # push stack value to segment[index]
                self.decrease_sp()
                self.save_current_stack_value_to_D()
                self.write(f"@R{general_reg}")
                self.write(f"A=M")
                self.write(f"M=D")
                
    def write_init(self):
        self.write("@256")
        self.write("D=A")
        self.write("@SP")
        self.write("M=D")
        self.write_call("Sys.init")
    
    def write_label(self, label):
        self.write(f"({self.vm_filename}:{label})")
    
    def write_goto(self, label):
        self.write(f"@{self.vm_filename}:{label}")
        self.write("0;JMP")
    
    def write_if(self,label):
        self.decrease_sp()
        self.save_current_stack_value_to_D()
        self.write(f"@{self.vm_filename}:{label}")
        self.write("D;JNE")
    
    def write_function(self, fn_name, n_locals):
        self.write(f"({fn_name})")
        for _ in range(int(n_locals)):
            self.write("@SP")
            self.write("A=M")
            self.write("M=0")
            self.increase_sp()

    def write_call(self, call_fn, n_args=0):
        # declare return address
        ret_addr = f"{call_fn}RET.{self.n_return}"
        self.n_return += 1
        
        # save return address to stack
        self.write(f"@{ret_addr}")
        self.write("D=A")
        self.write(f"@SP")
        self.write("A=M")
        self.write("M=D")
        self.increase_sp()
        
        # push "LCL", "ARG", "THIS", "THAT"
        for segment in ["LCL", "ARG", "THIS", "THAT"]:
            self.write(f"@{segment}")
            self.write("D=M")
            self.save_and_inc_stack()

        # ARG = SP-n-5
        self.write(f"@{int(n_args) + 5}")
        self.write("D=A")
        self.write("@SP")
        self.write("D=M-D")
        self.write("@ARG")
        self.write("M=D")

        # LCL = SP
        self.write("@SP")
        self.write("D=M")
        self.write("@LCL")
        self.write("M=D")
        
        # goto f
        self.write(f"@{call_fn}")
        self.write("0;JMP")
        
        # (return-address)
        self.write(f"({ret_addr})")
        

    def write_return(self):
        frame = "R13"
        ret = "R14"
        
        # FRAME = LCL
        self.write("@LCL")
        self.write("D=M")
        self.write(f"@{frame}")
        self.write("M=D")
    
        # RET = *(FRAME-5)
        self.write("@5")
        self.write("D=A")
        self.write(f"@{frame}")
        # self.write("D=M-D")
        self.write("A=M-D")
        self.write("D=M")
        self.write(f"@{ret}")
        self.write("M=D")
        
        # *ARG = pop()
        self.write_push_pop("pop", "argument")
        # self.decrease_sp()
        # self.write("@SP")
        # self.write("A=M")
        # self.write("D=M")
        # self.write("@ARG")
        # self.write("A=M")
        # self.write("M=D")

        # SP = ARG+1
        self.write("@ARG")
        self.write("D=M+1")
        self.write("@SP")
        self.write("M=D")
        
        # THAT = *(FRAME-1)
        # THIS = *(FRAME-2)
        # ARG = *(FRAME-3) 
        # LCL = *(FRAME-4) 
        for i, segment in enumerate(["THAT", "THIS", "ARG", "LCL"]):
            offset = i + 1
            self.write(f"@{offset}")
            self.write("D=A")
            self.write(f"@{frame}")
            self.write("A=M-D")
            self.write("D=M")
            self.write(f"@{segment}")
            self.write("M=D")
            
        # goto RET 
        self.write(f"@{ret}")
        self.write(f"A=M")
        self.write(f"0;JMP")
        
    # utility methods
    def increase_sp(self):
        self.write("@SP")
        self.write("M=M+1")
    
    def decrease_sp(self):
        self.write("@SP")
        self.write("M=M-1")
        
    def save_and_inc_stack(self):
        self.write("@SP")
        self.write("A=M")
        self.write("M=D")
        self.increase_sp()
    
    def save_current_stack_value_to_D(self):
        self.write("@SP")
        self.write("A=M")
        self.write("D=M")
    
    def point_segment_addr(self, segment, index):
        address = self.mem_map[segment]
        match segment:
            case "pointer" | "temp":
                self.write(f"@R{address+int(index)}")
            case "static":
                self.write(f"@{self.vm_filename}.{index}")
            case _:
                self.write(f"@{index}")
                self.write("D=A")
                self.write(f"@{address}")
                self.write("D=M+D")
                self.write("A=D")
    
    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self

    def __exit__(self, *args, **kargs):
        if self.file:
            self.file.close()
