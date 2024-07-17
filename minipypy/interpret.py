import frontend
from opcode import Bytecodes, opmap, opname


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
        self.env[var] = self.stack[self.stack_ptr]
        self.stack_ptr -= 1

    def LOAD_NAME(self):
        operand1 = ord(self.code.co_code[self.pc])
        operand2 = ord(self.code.co_code[self.pc + 1])
        self.pc += 2

        var = self.code.co_names[operand1]
        self.stack_ptr += 1
        self.stack[self.stack_ptr] = self.env[var]

    def BINARY_ADD(self):
        w_y = self.stack[self.stack_ptr]
        self.stack_ptr -= 1
        w_x = self.stack[self.stack_ptr]
        self.stack_ptr -= 1

        w_z = w_x.add(w_y)

        self.stack_ptr += 1
        self.stack[self.stack_ptr] = w_z

    def YIELD_FROM(self):
        pass

    def LOAD_BUILD_CLASS(self):
        "Load bultin module"
        pass

    def RETURN_VALUE(self):
        w_x = self.stack[self.stack_ptr]
        self.stack_ptr -= 1
        return w_x

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
            elif opcode == Bytecodes.YIELD_FROM:
                pass
            elif opcode == Bytecodes.LOAD_BUILD_CLASS:
                pass


if __name__ == "__main__":
    import sys

    code = frontend.load_pyc_py2(sys.argv[1])
    pyframe = PyFrame(code)
    w_x = pyframe.interpret()
