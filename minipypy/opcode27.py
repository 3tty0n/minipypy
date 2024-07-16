opmap = {}
opname = ['<%r>' % (op,) for op in range(256)]

def def_op(name, op):
    opname[op] = name
    opmap[name] = op

# cf. https://unpyc.sourceforge.net/Opcodes.html

def_op('STORE_CODE', 0x00)
def_op('POP_TOP', 0x01)
def_op('ROT_TWO', 0x02)
def_op('ROT_THREE', 0x03)
def_op('DUP_TOP', 0x04)
def_op('ROT_FOUR', 0x05)

def_op('NOP', 0x09)
def_op('UNARY_POSITIVE', 0x0a)
def_op('UNARY_NEGATIVE', 0x0b)
def_op('UNARY_NOT', 0x0c)
def_op('UNARY_CONVERT', 0x0d)
def_op('UNARY_INVERZT', 0x0f)

def_op('LIST_APPEND', 0x12)
def_op('BINARY_POWER', 0x13)
def_op('BINARY_MULTIPLY', 0x14)
def_op('BINARY_DIVIDE', 0x15)
def_op('BINARY_MODULO', 0x16)
def_op('BINARY_ADD', 0x17)
def_op('BINARY_SUBTRACT', 0x18)
def_op('BINARY_SUBSCR', 0x19)
def_op('BINARY_FLOOR_DIVIDE', 0x1a)
def_op('BINARY_TRUE_DIVIDE', 0x1b)
def_op('INPLACE_FLOOR_DIVIDE', 0x1c)
def_op('INPLACE_TRUE_DIVIDE', 0x1d)

def_op('SLICE', 0x1e)
def_op('SLICE1', 0x1f)
def_op('SLICE2', 0x20)
def_op('SLICE3', 0x21)

def_op('STORE_SLICE', 0x28)
def_op('STORE_SLICE1', 0x29)
def_op('STORE_SLICE2', 0x2a)
def_op('STORE_SLICE3', 0x2b)

def_op('DELETE_SLICE', 0x32)
def_op('DELETE_SLICE1', 0x33)
def_op('DELETE_SLICE2', 0x34)
def_op('DELETE_SLICE3', 0x35)

def_op('INPLACE_ADD', 0x37)
def_op('INPLACE_SUBTRACT', 0x38)
def_op('INPLACE_MULTIPLY', 0x39)
def_op('INPLACE_DIVIDE', 0x3a)
def_op('INPLACE_MODULO', 0x3b)
def_op('STORE_SUBSCR', 0x3c)
def_op('DELETE_SUBSCR', 0x3d)
def_op('BINARY_LSHIFT', 0x3e)
def_op('BINARY_RSHIFT', 0x3f)
def_op('BINARY_AND', 0x40)
def_op('BINARY_XOR', 0x41)
def_op('BINARY_OR', 0x42)
def_op('INPLACE_POWER', 0x43)
def_op('GET_ITER', 0x44)

def_op('PRINT_EXPR', 0x46) # used only in interactive mode
def_op('PRINT_ITEM', 0x47)
def_op('PRINT_NEWLINE', 0x48)
def_op('PRINT_ITEM_TO', 0x49)
def_op('PRINT_NEWLINE_TO', 0x4a)
def_op('INPLACE_LSHIFT', 0x4b)
def_op('INPLACE_RSHIFT', 0x4c)
def_op('INPLACE_AND', 0x4d)
def_op('INPLACE_XOR', 0x4e)
def_op('INPLACE_OR', 0x4f)
def_op('BREAK_LOOP', 0x50)
def_op('WITH_CLEANUP', 0x51)
def_op('LOAD_LOCALS', 0x52)
def_op('RETURN_VALUE', 0x53)
def_op('IMPORT_STAR', 0x54)
def_op('EXEC_STMT', 0x55)
def_op('YIELD_VALUE', 0x56)
def_op('POP_BLOCK', 0x57)
def_op('END_FINALLY', 0x58)
def_op('BUILD_CLASS', 0x59)

# 2 operands
def_op('STORE_NAME', 0x5a)      # implementes name = TOS
def_op('DELETE_NAME', 0x5b)     # implementes del name
def_op('UNPACK_SEQUENCE', 0x5c) # Unpacks tos into individual values
def_op('FOR_ITER', 0x5d)        # TOS is an iterator. Call its next() method. If this yields a new value, push it on the stack (leaving the iterator below it).
def_op('STORE_ATTR', 0x5f)      # Implements TOS.name = TOS1, where /namei/ is the index of name in co_names.

def_op('DELETE_ATTR', 0x60)     # Implements del TOS.name, using /namei/ as index into co_names.
def_op('STORE_GLOBAL', 0x61)
def_op('DELETE_GLOBAL', 0x62)
def_op('DUP_TOPX', 0x63)        # NOTE: no operand
def_op('LOAD_CONST', 0x64)
def_op('LOAD_NAME', 0x65)
def_op('BUILD_TUPLE', 0x66)
def_op('BUILD_LIST', 0x67)
def_op('BUILD_MAP', 0x68)
def_op('LOAD_ATTR', 0x69)
def_op('COMPARE_OP', 0x6a)      # Performs a Boolean operation. The operation name can be found in cmp_op[/opname/].
def_op('IMPORT_NAME', 0x6b)
def_op('IMPORT_FROM', 0x6c)

def_op('JUMP_FORWARD', 0x6e)
def_op('JUMP_IF_FALSE', 0x6f)
def_op('JUMP_IF_TRUE', 0x70)
def_op('JUMP_ABSOLUTE', 0x71)

def_op('LOAD_GLOBAL', 0x74)

def_op('CONTINUE_LOOP', 0x77)
def_op('SETUP_LOOP', 0x78)
def_op('SETUP_EXCEPT', 0x79)
def_op('SETUP_FINALLY', 0x7a)

def_op('LOAD_FAST', 0x7c)       # Pushes a reference to the local co_varnames[/var_num/] onto the stack.
def_op('STORE_FAST', 0x7d)      # Stores TOS into the local co_varnames[/var_num/].
def_op('DELETE_FAST', 0x7e)     # Deletes local co_varnames[/var_num/].

def_op('RAISE_VARARGS', 0x82)

# Calls a function. The low byte of /argc/ indicates the number of positional parameters,
# the high byte the number of keyword parameters. On the stack, the opcode finds the
# keyword parameters first. For each keyword argument, the value is on top of the
# key. Below the keyword parameters, the positional parameters are on the stack, with the
# right-most parameter on top. Below the parameters, the function object to call is on the
# stack.
def_op('CALL_FUNCTION', 0x83)
# Pushes a new function object on the stack. TOS is the code associated with the
# function. The function object is defined to have /argc/ default parameters, which are
# found below TOS.
def_op('MAKE_FUNCTION', 0x84)
def_op('BUILD_SLICE', 0x85)
def_op('MAKE_CLOSURE', 0x86)
def_op('LOAD_CLOSURE', 0x87)
def_op('LOAD_DEREF', 0x88)
def_op('STORE_DEREF', 0x89)

def_op('CALL_FUNCTION_VAR', 0x8c)
def_op('CALL_FUNCTION_KW', 0x8d)
def_op('CALL_FUNCTION_VAR_KW', 0x8e)
def_op('EXTENDED_ARGS', 0x8f)
