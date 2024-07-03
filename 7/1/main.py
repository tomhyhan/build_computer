import sys
import os
from vm_parser import Parser
from writer import CodeWriter

if __name__ == "__main__":
    filepath = sys.argv[1]
    # temp
    # base_path = "./MemoryAccess/BasicTest/"
    filename = os.path.splitext(os.path.basename(filepath))[0]
    
    base_path = os.path.dirname(filepath)
    output_file_name = f"{filename}.asm"
    
    output_file_path = os.path.join(base_path, output_file_name) 

    p = Parser(filepath)
    with CodeWriter(output_file_path) as cw:
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
            p.advance()