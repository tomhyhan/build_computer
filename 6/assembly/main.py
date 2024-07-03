from parse import Parse, CommandType
from code import Code
from symtab import Symtab
import sys

def main():
    try:
        file_path = sys.argv[1]
    except IndexError:
        print("sys arg not provide")
        exit(1)
    
    p = Parse(file_path)
    symtab = Symtab()
    pc = 0
    commands = []
    while p.has_more_commands():
        if p.command_type() == CommandType.A_COMMAND:
            commands.append([CommandType.A_COMMAND, p.symbol])
            pc += 1
        elif p.command_type() == CommandType.C_COMMAND:
            commands.append([CommandType.C_COMMAND, (p.dest, p.comp, p.jmp)])
            pc += 1
        elif p.command_type() == CommandType.L_COMMAND:
            symtab.symbols[p.symbol] = pc
        p.advance()

    pc = 0
    variable_addr = 16
    with open("a.hack", 'w') as f:
        for command in commands:
            c_type = command[0]
            if c_type == CommandType.A_COMMAND:
                sym = command[1]
                if not sym.isdigit():
                    if symtab.contains(sym):
                        sym = symtab.get_address(sym)
                    else:
                        symtab.add_entry(sym, variable_addr)  
                        sym = variable_addr
                        variable_addr += 1
                b = Code.sym_to_b(sym)    
                f.writelines(b + '\n')
                pc += 1
            elif c_type == CommandType.C_COMMAND:
                dest, comp, jmp = command[1]
                b = "111" + Code.comp(comp) + Code.dest(dest) + Code.jmp(jmp)
                f.writelines(b + '\n')
                pc += 1


if "__main__" == __name__:
    main()