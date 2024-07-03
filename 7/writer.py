import os

class CodeWriter:
    def __init__(self, filename, mode='a', debug=True):
        self.filename = filename
        self.mode = mode 
        self.line_num = 0  
        self.debug = debug
        self.n_cmp_fn = 0
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
            "general": 13
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
        
    def write_push_pop(self, command, segment, index):
        # argument, local, static, constant,
        # this, that, pointer,
        # temp
        match command:
            case "push":
                if segment == "constant":
                    # get constant value
                    self.write(f"@{index}")
                    self.write("D=A")
                    
                    self.save_to_stack()
                else:
                    self.point_segment_addr(segment, index)

                    # get value of segment
                    self.write("D=M")

                    self.save_to_stack()
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
                
            
    # utility methods
    def increase_sp(self):
        self.write("@SP")
        self.write("M=M+1")
    
    def decrease_sp(self):
        self.write("@SP")
        self.write("M=M-1")
        
    def save_to_stack(self):
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
