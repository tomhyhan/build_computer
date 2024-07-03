import os

class CodeWriter:
    def __init__(self, filename, mode='w'):
        self.filename = filename
        self.vm_filename = None
        self.mode = mode
        self.cmp_cnt = 0
        # general reg
        self.addr = "addr"
        self.cmp_mapping = {
            "eq" : "JEQ",
            "gt" : "JGT",
            "lt" : "Jlt",
        }
        self.segment_base_addr = {
            "constant" : "SP",
            "local": "LCL",
            "argument": "ARG",
            "this": "THIS",
            "that": "THAT",
            "temp": 5,
            "pointer": 3,
            "addr": 13,
            "static" : 16,
        }
        
        
    def set_filename(self, vm_path):
        self.vm_filename = os.path.splitext(os.path.basename(vm_path))[0]

    def write_line(self, content):
        self.file.write(f"{content}\n")

    def write_arithmetic(self, command):

        if command not in ['neg', 'not']:
            self.save_prev_to_D()
            
        self.decrease_sp()
        self.points_sp_to_address()

        match command:
            case "add":
                self.write_line("M=D+M")
            case "sub":
                self.write_line("M=M-D")
            case "and":
                self.write_line("M=D&M")
            case "or":
                self.write_line("M=D|M")
            case "neg":
                self.write_line("M=-M")
            case "not":
                self.write_line("M=!M")
            case "eq" | "gt" | "lt":
                self.write_line("D=D-M")
                
                self.write_line(f"@CMP{self.cmp_cnt}")
                self.write_line(f"D;{self.cmp_mapping[command]}")
                
                self.points_sp_to_address()
                self.write_line("M=0")
                self.write_line(f"@CMPEND{self.cmp_cnt}")
                self.write_line("0;JMP")

                self.write_line(f"(CMP{self.cmp_cnt})")
                self.points_sp_to_address()
                self.write_line("M=-1")

                self.write_line(f"(CMPEND{self.cmp_cnt})")
                self.cmp_cnt += 1
        self.increase_sp()
    
    def points_sp_to_address(self):
        self.write_line("@SP")
        self.write_line("A=M")
    
    def points_reg_to_address(self, segment):
        self.write_line(f"@{self.segment_base_addr[segment]}")
        self.write_line("A=M")
    
    def save_prev_to_D(self):
        self.decrease_sp()
        self.write_line("@SP")
        self.write_line("A=M")
        self.write_line("D=M")
    
    def increase_sp(self):
        self.write_line("@SP")
        self.write_line("M=M+1")

    def increase_reg(self, segment):
        self.write_line(f"@{self.segment_base_addr[segment]}")
        self.write_line("M=M+1")

    def decrease_sp(self):
        self.write_line("@SP")
        self.write_line("M=M-1")
    
    def fetch_address(self, segment, index):
        segment_addr = self.segment_base_addr[segment]
        
        match segment:
            case "temp" | "pointer":
                self.write_line(f"@R{segment_addr+int(index)}")
            case "static":
                self.write_line(f"@R{self.vm_filename}.{index}")
            case _:
                self.write_line(f"@{index}")
                self.write_line("D=A")
                self.write_line(f"@{segment_addr}")
                self.write_line("A=M+D")
    
    def write_push_pop(self, command, segment, index):
        # LCL - local, SP - constant, ARG - argument, THIS - this, THAT - that RAM[5-12] = temp, RAM[13-15] - general
        # push constant 10 
        # change it => sp -> relative addr, reg -> base addr
        # operations => sp, local, constant, argument, this that, temp, pointer, general
        match command:
            case "push":               
                # constant
                if segment == "constant":
                    self.write_line(f"@{index}")
                    self.write_line("D=A")
                    self.save_to_stack()
                # local, arg, this, that and others..
                else:
                    self.fetch_address(segment, index)
                    self.write_line("D=M")
                    self.save_to_stack()    
            case "pop":
                assert(command != "constant")
                temp_addr = self.segment_base_addr[self.addr]
                # fetch address 
                self.fetch_address(segment, index)
                self.write_line("D=A")
                # save to temp
                self.write_line(f"@{temp_addr}")
                self.write_line(f"M=D")
                 
                self.decrease_sp()
                self.write_line("A=M")
                self.write_line("D=M")
                self.write_line(f"@{temp_addr}")
                self.write_line("A=M")
                self.write_line("M=D")
    
    def save_to_stack(self):
        self.points_sp_to_address()
        self.write_line("M=D")
        self.increase_sp()
    
    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self

    def __exit__(self, *args, **kargs):
        if self.file:
            self.file.close()
