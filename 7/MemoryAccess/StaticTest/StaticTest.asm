// push constant 111
@111 // 0
D=A // 1
@SP // 2
A=M // 3
M=D // 4
@SP // 5
M=M+1 // 6
// push constant 333
@333 // 7
D=A // 8
@SP // 9
A=M // 10
M=D // 11
@SP // 12
M=M+1 // 13
// push constant 888
@888 // 14
D=A // 15
@SP // 16
A=M // 17
M=D // 18
@SP // 19
M=M+1 // 20
// pop static 8
@StaticTest.8 // 21
D=A // 22
@R13 // 23
M=D // 24
@SP // 25
M=M-1 // 26
@SP // 27
A=M // 28
D=M // 29
@R13 // 30
A=M // 31
M=D // 32
// pop static 3
@StaticTest.3 // 33
D=A // 34
@R13 // 35
M=D // 36
@SP // 37
M=M-1 // 38
@SP // 39
A=M // 40
D=M // 41
@R13 // 42
A=M // 43
M=D // 44
// pop static 1
@StaticTest.1 // 45
D=A // 46
@R13 // 47
M=D // 48
@SP // 49
M=M-1 // 50
@SP // 51
A=M // 52
D=M // 53
@R13 // 54
A=M // 55
M=D // 56
// push static 3
@StaticTest.3 // 57
D=M // 58
@SP // 59
A=M // 60
M=D // 61
@SP // 62
M=M+1 // 63
// push static 1
@StaticTest.1 // 64
D=M // 65
@SP // 66
A=M // 67
M=D // 68
@SP // 69
M=M+1 // 70
// sub
@SP // 71
M=M-1 // 72
@SP // 73
A=M // 74
D=M // 75
@SP // 76
M=M-1 // 77
@SP // 78
A=M // 79
M=M-D // 80
@SP // 81
M=M+1 // 82
// push static 8
@StaticTest.8 // 83
D=M // 84
@SP // 85
A=M // 86
M=D // 87
@SP // 88
M=M+1 // 89
// add
@SP // 90
M=M-1 // 91
@SP // 92
A=M // 93
D=M // 94
@SP // 95
M=M-1 // 96
@SP // 97
A=M // 98
M=M+D // 99
@SP // 100
M=M+1 // 101
