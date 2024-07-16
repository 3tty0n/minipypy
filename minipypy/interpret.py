import frontend

def interpret(code):
    bytecode = code.co_code
    stacksize = code.co_stacksize
    stack = [None] * stacksize
    stack_ptr = -1
    pc = 0
    while pc < len(bytecode):
        opcode = bytecode[pc]
        print(opcode)
        pc += 1


if __name__ == '__main__':
    import sys
    code = frontend.load_pyc(sys.argv[1])
    interpret(code)
