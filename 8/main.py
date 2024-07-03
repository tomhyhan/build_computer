import sys
import os
from vm_parser import Parser
from writer import CodeWriter

if __name__ == "__main__":
    base_path = sys.argv[1]
    vm_files = [file for file in os.listdir(base_path) if file.endswith(".vm")]
    
    dirname = os.path.basename(base_path)
    output_file_name = f"{dirname}.asm"
    output_file_path = os.path.join(base_path, output_file_name) 
    
    if os.path.exists(output_file_path):
        os.remove(output_file_path)
        print("creating new file...")
                
    with CodeWriter(output_file_path, mode='a', debug=True) as cw:
        if "Sys.vm" in vm_files:
            print("init wrote")
            cw.write_init()
        for vm_file in vm_files:
            filepath = os.path.join(base_path, vm_file)
            p = Parser(filepath)
            cw.set_filename(filepath)  
            while p.has_more_commands():
                cw.file.write(f"// {p.current_instruction}\n")
                match p.commandType():
                    case Parser.C_ARITHMETIC:
                        command = p.arg1
                        cw.write_arithmetic(command)
                    case Parser.C_PUSH | Parser.C_POP:
                        command = "push" if p.commandType() == Parser.C_PUSH else "pop"
                        segment, index = p.arg1, p.arg2
                        cw.write_push_pop(command, segment, index)
                    case Parser.C_IF:
                        label = p.arg1
                        cw.write_if(label)
                    case Parser.C_LABEL:
                        label = p.arg1
                        cw.write_label(label)
                    case Parser.C_GOTO:
                        label = p.arg1
                        cw.write_goto(label)
                    case Parser.C_FUNCTION:
                        label, n_locals= p.arg1, p.arg2
                        cw.write_function(label, n_locals)
                    case Parser.C_CALL:
                        label, n_args = p.arg1, p.arg2
                        cw.write_call(label, n_args)
                    case Parser.C_RETURN:
                        cw.write_return()
                p.advance()