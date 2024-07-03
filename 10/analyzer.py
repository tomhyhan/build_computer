import sys
import os
from compilation_engine import CompilationEngine
from tokenizer import Tokenizer
from symtab import Symtab
from vmwriter import VMwriter
def main():
    base_path = sys.argv[1]
    jack_files = [file for file in os.listdir(base_path) if file.endswith(".jack")]
    
    for jack_file in jack_files:
        output_file_name = f"{jack_file.split('.')[0]}$.xml"
        output_file_path = os.path.join(base_path, output_file_name) 
        
        if os.path.exists(output_file_path):
            os.remove(output_file_path)
            print("creating new file...")
        
        input_file_path = os.path.join(base_path, jack_file)
        tokenizer = Tokenizer(input_file_path)
        symtab = Symtab()
        
        vm_file_name = f"{jack_file.split('.')[0]}.vm"
        vm_file_path = os.path.join(base_path, vm_file_name)
        # create_test_tokens_xml(base_path, jack_file, tokenizer)
        with VMwriter(vm_file_path, 'w') as vm_writer:
            with CompilationEngine(output_file_path, tokenizer, symtab, vm_writer, 'w') as engine:
                engine.compile_class()
    
        print("end...")
    
def create_test_tokens_xml(base_path, jack_file, tokenizer: Tokenizer):
    output_file_name = f"{jack_file.split('.')[0]}$T.xml"
    output_file_path = os.path.join(base_path, output_file_name) 
    with open(output_file_path, 'w') as f:
        f.write("<tokens>\n")
        while tokenizer.has_more_tokens():
            # print(tokenizer.token)
            token_type = tokenizer.token_type()
            token = tokenizer.token
            f.write(f"<{token_type}> {token} </{token_type}>\n")
            tokenizer.advance()
        f.write("</tokens>\n")

if __name__ == "__main__":
    main()
    pass