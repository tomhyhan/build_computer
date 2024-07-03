// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

(KEYPRESSED)
    @SCREEN
    D = A
    @scrnAddr
    M = D // save screen address

(KEYBOARD)
    @KBD
    D=M
    @BLACK
    D;JNE
    @WHITE
    D;JEQ

(BLACK)
    @color
    M=-1
    @DRAW
    0;JMP

(WHITE)
    @color
    M=0
    @DRAW
    0;JMP

(DRAW)
    @color
    D=M
    
    @scrnAddr
    A = M
    M = D

    @scrnAddr
    D = M + 1
    @KBD
    D = A - D

    @scrnAddr
    M = M + 1
    A = M

    @DRAW
    D;JGT

    @KEYPRESSED
    0;JMP