import sys
import types

import frontend
from minipypy.objects.baseobject import *
from minipypy.objects.pycode import PyCode
from minipypy.opcode27 import Bytecodes, opmap, opname


class PyFrame(object):

    def __init__(self, code):
        self.code = code
        self.stack = [None] * 8
        self.stack_ptr = -1
        self.locals_cells_stack_w = [None] * 8
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

    def create_pyframe(self, code, args):
        pyframe = PyFrame(code)
        for i in range(len(args)):
            pyframe.locals_cells_stack_w[i] = args[i]
        return pyframe

    def read_const(self, operand):
        return self.code.co_consts[operand]

    def read_operand(self):
        operand = ord(self.code.co_code[self.pc])
        self.pc += 2
        return operand

    def POP_TOP(self):
        self.pop()

    def STORE_NAME(self):
        operand1 = self.read_operand()

        var = self.code.co_names[operand1]
        self.env[var] = self.pop()

    def STORE_FAST(self):
        operand1 = self.read_operand()
        w_x = self.pop()
        self.locals_cells_stack_w[operand1] = w_x

    def LOAD_NAME(self):
        operand1 = self.read_operand()

        var = self.code.co_names[operand1]
        self.push(self.env[var])

    def LOAD_FAST(self):
        operand1 = self.read_operand()
        w_x = self.locals_cells_stack_w[operand1]
        self.push(w_x)

    def LOAD_CONST(self):
        operand1 = self.read_operand()

        const = self.read_const(operand1)
        if not const:
            self.push(W_None())
        elif isinstance(const, W_Root):
            self.push(const)
        else:
            raise Exception("Unimplemented pattern", const)

    def BINARY_POWER(self):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.power(w_y)
        self.push(w_z)

    def BINARY_MULTIPLY(self):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.mul(w_y)
        self.push(w_z)

    def BINARY_DIVIDE(self):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.div(w_y)
        self.push(w_z)

    def BINARY_MODULO(self):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.mod(w_y)
        self.push(w_z)

    def BINARY_ADD(self):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.add(w_y)
        self.push(w_z)

    def BINARY_SUBTRACT(self):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.sub(w_y)
        self.push(w_z)

    def BINARY_SUBSCR(self):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.subscr(w_y)
        self.push(w_z)

    def BINARY_FLOOR_DIVIDE(self):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.div(w_y) # TODO: floor
        self.push(w_z)

    def BINARY_TRUE_DIVIDE(self):
        w_y = self.pop()
        w_x = self.pop()
        w_z = w_x.true_div(w_y)
        self.push(w_z)

    def RETURN_VALUE(self):
        return self.pop()

    def MAKE_FUNCTION(self):
        argc = self.read_operand()

        code = self.pop()
        arg_defaults = [None] * argc
        i = 0
        while i < argc:
            arg_defaults[i] = self.pop()
            i += 1
        w_function = W_Function(code, arg_defaults)
        self.push(w_function)

    def CALL_FUNCTION(self):
        argc = self.read_operand()

        kwnum = argc >> 8
        argnum = argc & 0xff
        args = [None] * argnum
        for i in range(argnum):
            args[i] = self.pop()
        w_function = self.pop()
        assert isinstance(w_function, W_Function)
        pyframe = self.create_pyframe(w_function.body, args)
        w_value = pyframe.interpret()
        if w_value:
            self.push(w_value)

    def PRINT_ITME(self):
        w_x = self.pop()
        print w_x,

    def PRINT_NEWLINE(self):
        print

    def interpret(self):
        while self.pc < len(self.code.co_code):
            opcode = ord(self.code.co_code[self.pc])
            self.pc += 1

            print(opcode, opname[opcode], self.stack, self.stack_ptr, self.locals_cells_stack_w)
            if opcode == Bytecodes.LOAD_CONST:
                self.LOAD_CONST()
            elif opcode == Bytecodes.BINARY_ADD:
                self.BINARY_ADD()
            elif opcode == Bytecodes.BINARY_DIVIDE:
                self.BINARY_DIVIDE()
            elif opcode == Bytecodes.LOAD_NAME:
                self.LOAD_NAME()
            elif opcode == Bytecodes.LOAD_FAST:
                self.LOAD_FAST()
            elif opcode == Bytecodes.STORE_NAME:
                self.STORE_NAME()
            elif opcode == Bytecodes.STORE_FAST:
                self.STORE_FAST()
            elif opcode == Bytecodes.RETURN_VALUE:
                return self.RETURN_VALUE()
            elif opcode == Bytecodes.PRINT_ITEM:
                self.PRINT_ITME()
            elif opcode == Bytecodes.PRINT_NEWLINE:
                self.PRINT_NEWLINE()
            elif opcode == Bytecodes.MAKE_FUNCTION:
                self.MAKE_FUNCTION()
            elif opcode == Bytecodes.CALL_FUNCTION:
                self.CALL_FUNCTION()
            elif opcode == Bytecodes.POP_TOP:
                self.POP_TOP()
            elif opcode == Bytecodes.STOP_CODE:
                pass


if __name__ == "__main__":
    import sys
    import dis

    code = frontend.rpy_load_py2(sys.argv[1])
    pyframe = PyFrame(code)
    w_x = pyframe.interpret()
