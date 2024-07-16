import frontend
from opcode import Bytecodes, opmap

def interpret(code):
    bytecode = code.co_code
    stacksize = code.co_stacksize
    stack = [None] * stacksize
    stack_ptr = -1
    pc = 0
    while pc < len(bytecode):
        opcode = ord(bytecode[pc])
        if opcode == Bytecodes.LOAD_CONST:
            pass
        elif opcode == Bytecodes.BINARY_ADD:
            pass
        elif opcode == Bytecodes.LOAD_NAME:
            pass
        elif opcode == Bytecodes.STORE_NAME:
            pass
        elif opcode == Bytecodes.RETURN_VALUE:
            pass
        elif opcode == Bytecodes.YIELD_FROM:
            pass
        elif opcode == Bytecodes.LOAD_BUILD_CLASS:
            pass
        pc += 1


if __name__ == '__main__':
    import sys
    code = frontend.load_pyc_py2(sys.argv[1])
    interpret(code)
