class Symtab:
    """
        handling variables:
            code generator - symtab
            
            1. we have two sym tables: 
                1. class level symtab
                2. subroutine level symbtab
                
            whenever we encounter a variabel we record it to the symtab. If we encounter the variable, we first look at the subroutine symtab, and then the class level symtab.
            
            2. For transoforming epression to vm_code:
                if exp is a number:
                    output push number
                    
                if exp is a variable:
                    output push var
                    
                if exp is exp1 op exp2:
                    codewrite(exp1)
                    codewrite(exp2)
                    output op
                    
                if exp is op exp:
                    codewrite(exp)
                    output op

                if exp is f(exp1, exp2 ...):
                    codewrite(exp1)
                    codewrite(exp2) ...
                    output call f 
                    
            3. let x = a + b - c 
                => push a | push b | + | push c | - | pop x
                
            4. If else:                 while:
                    exp1                    L1:
                    not                         exp1
                    if goto L1                  not
                    state1                      if goto L2
                    goto L2                     state1
                    L1:                         goto L1
                        state2              L2:
                    L2:
                        ...
            
            5.  pointer 0 / THIS
                pointer 1 / THAT
                
                Using pointer to anchor heap address in RAM
                push 8000 -> pop pointer 0 ; set THIS to 8000
                
                push/pop this 0; RAM[8000]
                push/pop this 1; RAM[8001]
                push/pop this 2; RAM[8002]
                ...
                
            6. Handling objects
                caller: push arguments call the contructor and save the objects' base address to variable 
                callee: Create subroutine Symbol table. Computes memory size needed for object. Allocate a memory address as a base address of the object using OS. Save the base address to pointer 0 (THIS). Allocate arguments to THIS virtual stack and thus filling in the RAM memory. Return the base address.
            
    """
    
    def __init__(self):
        self.class_symtab = {}
        self.sub_symtab = {}
        
    def define(self):
        pass
    
    def var_count(self):
        pass
    
    def kindof(self):
        pass
    
    def typeof(self):
        pass
    
    def indexof(self):
        pass