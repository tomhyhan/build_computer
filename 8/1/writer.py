import os

class CodeWriter:
    def __init__(self, filename, mode='a'):
        self.filename = filename
        self.vm_filename = None
        self.mode = mode
        self.cmp_cnt = 0
        # general reg
        self.addr = "addr"
        self.frame = "frame"
        self.ret_addr = "ret_addr"
        self.frame = "frame"
        # return function address tracker
        self.n_return = 0
        
        self.cmp_mapping = {
            "eq" : "JEQ",
            "gt" : "JGT",
            "lt" : "JLT",
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
            "frame": 13,
            "ret_addr": 14,
            "static" : 16,
        }
    
    def write_init(self):
        self.write_line("@256")
        self.write_line("D=A")
        self.write_line("@SP")
        self.write_line("M=D")
        self.write_call("Sys.init", 0)
        
    def write_label(self, label):
        self.write_line(f"({self.vm_filename}${label})")
    
    def write_goto(self, label):
        self.write_line(f"@{self.vm_filename}${label}")    
        self.write_line(f"0;JMP")    
    
    def write_if(self, label):
        self.save_prev_to_D()
        self.write_line(f"@{self.vm_filename}${label}")
        self.write_line(f"D;JNE")
        
    def write_call(self, label, n_args):
        ret_addr = f"{label}$RET.{self.n_return}"
        self.n_return += 1
        
        # push return-address
        self.write_line(f"@{ret_addr}")
        self.write_line("D=A")
        self.write_line("@SP")
        self.write_line("A=M")
        self.write_line("M=D")
        self.increase_sp()
        
        # push LCL   
        # push ARG  
        # push THIS 
        # push THAT 
        for segment in ["LCL", "ARG", "THIS", "THAT"]:
            self.write_line(f"@{segment}")
            self.write_line("D=M")
            self.write_line("@SP")
            self.write_line("A=M")
            self.write_line("M=D")
            self.increase_sp()

        # ARG = SP-n-5
        self.write_line(f"@{int(n_args)+5}")
        self.write_line(f"D=A")
        self.write_line("@SP")
        self.write_line("D=M-D")
        self.write_line("@ARG")
        self.write_line("M=D")
        
        # LCL = SP
        self.write_line("@SP")
        self.write_line("D=M")
        self.write_line("@LCL")
        self.write_line("M=D")
        
        # goto f
        self.write_line(f"@{label}")
        self.write_line("0;JMP")

        # (return-address)
        self.write_line(f"({ret_addr})")
               
    def write_return(self):
        frame_addr = self.segment_base_addr[self.frame]
        ret_addr = self.segment_base_addr[self.ret_addr]
        
        # FRAME = LCL
        self.write_line("@LCL")
        self.write_line("D=M")
        self.write_line(f"@R{frame_addr}")
        self.write_line("M=D")
        
        # RET = *(FRAME-5)
        self.write_line(f"@R{frame_addr}")
        self.write_line(f"D=M")
        self.write_line("@5")
        self.write_line(f"D=D-A")
        self.write_line(f"A=D")
        self.write_line(f"D=M")
        self.write_line(f"@R{ret_addr}")
        self.write_line(f"M=D")

        # *ARG = pop()
        self.decrease_sp()
        self.write_line("A=M")
        self.write_line("D=M")
        self.write_line("@ARG")
        self.write_line("A=M")
        self.write_line("M=D")
        
        # SP = ARG+1
        self.write_line("@ARG")
        self.write_line("D=M")
        self.write_line("@SP")
        self.write_line("M=D+1")
        
        # THAT = *(FRAME-1) 
        # THIS = *(FRAME-2) 
        # ARG = *(FRAME-3) 
        # LCL = *(FRAME-4)
        for i, segment in enumerate(["THAT", "THIS", "ARG", "LCL"]):
            offset = i + 1
            self.write_line(f"@{offset}")
            self.write_line("D=A")
            self.write_line(f"@{frame_addr}")
            self.write_line("D=M-D")
            self.write_line("A=D")
            self.write_line("D=M")
            self.write_line(f"@{segment}")
            self.write_line("M=D")

        self.write_line(f"@R{ret_addr}")
        self.write_line(f"A=M")
        self.write_line("0;JMP")
                      
    def write_function(self, label, n_locals):
        self.write_line(f"({label})")
        for _ in range(int(n_locals)):
            self.push_0()
            self.increase_sp()   
                 
    def push_0(self):
        self.write_line("@SP")
        self.write_line("A=M")
        self.write_line("M=0")
                
    def set_filename(self, vm_path):
        self.vm_filename = os.path.splitext(os.path.basename(vm_path))[0]

    def write_line(self, content):
        self.file.write(f"{content}\n")
   
    def set_A_to_stack(self):
        self.write_line('@SP')
        self.write_line('A=M')
        
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
                self.write_line("M=M&D")
            case "or":
                self.write_line("M=D|M")
            case "neg":
                self.write_line("M=-M")
            case "not":
                self.write_line("M=!M")
            case "eq" | "gt" | "lt":
                self.write_line("D=M-D")
                
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
                self.write_line(f"@{segment_addr}")
                self.write_line("D=M")
                self.write_line(f"@{index}")
                self.write_line("A=D+A")
    
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
                    # self.push_D_to_stack()
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
