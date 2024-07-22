import sys

import frontend
from opcode27 import Bytecodes, opmap, opname


try:
    BUILTINS = sys.modules['__builtin__']
except:
    BUILTINS = sys.modules['builtins']


class W_Object(object):
    def __init__(self, value):
        self.value = value


class W_NoneObject(W_Object):
    def __init__(self):
        pass

    def __repr__(self):
        return "W_None()"


class W_IntObject(W_Object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "W_IntObject(%d)" % (self.value)

    def add(self, other):
        return W_IntObject(self.value + other.value)


class PyFrame(object):

    def __init__(self, code):
        self.code = code
        self.stack = [W_NoneObject()] * 8
        self.stack_ptr = -1
        self.pc = 0
        self.env = {}

    def pop(self):
        w_x = self.stack[self.stack_ptr]
        self.stack_ptr -= 1
        return w_x

    def push(self, w_x):
        self.stack_ptr += 1
        self.stack[self.stack_ptr] = w_x

    def top(self):
        return self.stack[self.stack_ptr]

    def read_const(self, operand):
        value = self.code.co_consts[operand]
        if not value:
            return W_NoneObject()
        elif isinstance(value, int):
            return W_IntObject(value)
        else:
            return W_Object(value)

    def LOAD_CONST(self):
        operand1 = ord(self.code.co_code[self.pc])
        operand2 = ord(self.code.co_code[self.pc + 1])
        self.pc += 2

        w_x = self.read_const(operand1)
        self.stack_ptr += 1
        self.stack[self.stack_ptr] = w_x

    def STORE_NAME(self):
        operand1 = ord(self.code.co_code[self.pc])
        operand2 = ord(self.code.co_code[self.pc + 1])
        self.pc += 2

        var = self.code.co_names[operand1]
        self.env[var] = self.pop()

    def LOAD_NAME(self):
        operand1 = ord(self.code.co_code[self.pc])
        operand2 = ord(self.code.co_code[self.pc + 1])
        self.pc += 2

        var = self.code.co_names[operand1]
        self.push(self.env[var])

    def BINARY_ADD(self):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.add(w_y)
        self.push(w_z)

    def RETURN_VALUE(self):
        w_x = self.stack[self.stack_ptr]
        self.stack_ptr -= 1
        return w_x

    def PRINT_ITME(self):
        w_x = self.pop()
        print w_x,

    def PRINT_NEWLINE(self):
        print

    def interpret(self):
        while self.pc < len(self.code.co_code):
            opcode = ord(code.co_code[self.pc])
            self.pc += 1

            print(opcode, opname[opcode])
            if opcode == Bytecodes.LOAD_CONST:
                self.LOAD_CONST()
            elif opcode == Bytecodes.BINARY_ADD:
                self.BINARY_ADD()
            elif opcode == Bytecodes.LOAD_NAME:
                self.LOAD_NAME()
            elif opcode == Bytecodes.STORE_NAME:
                self.STORE_NAME()
            elif opcode == Bytecodes.RETURN_VALUE:
                return self.RETURN_VALUE()
            elif opcode == Bytecodes.PRINT_ITEM:
                self.PRINT_ITME()
            elif opcode == Bytecodes.PRINT_NEWLINE:
                self.PRINT_NEWLINE()
            elif opcode == Bytecodes.MAKE_FUNCTION:
                self.pc += 2
            elif opcode == Bytecodes.CALL_FUNCTION:
                self.pc += 2


if __name__ == "__main__":
    import sys
    import dis

    code = frontend.compile_py2(sys.argv[1])
    pyframe = PyFrame(code)
    w_x = pyframe.interpret()
