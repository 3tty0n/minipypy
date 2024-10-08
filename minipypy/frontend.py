import binascii
import marshal
import py
import struct
import sys
import time

from rpython.rlib.debug import debug_print
from rpython.rlib.rfile import create_file
from rpython.rlib.jit import not_rpython

from minipypy.module.marshal import unmarshal_pycode


@not_rpython
def load_pyc_py3(fname):
    f = open(fname, "rb")
    magic = f.read(4)
    magic = binascii.hexlify(magic)
    read_date_and_size = True
    flags = struct.unpack("<L", f.read(4))[0]
    hash_based = bool(flags & 0x01)
    check_source = bool(flags & 0x02)
    debug_print("flags %s" % (flags))
    if hash_based:
        source_hash = f.read(8)
        read_date_and_size = False
        hash = binascii.hexlify(source_hash)
        debug_print("hash " + str(hash))
        debug_print("check_source " + str(check_source))
    if read_date_and_size:
        moddate = f.read(4)
        modtime = time.asctime(time.localtime(struct.unpack("<L", moddate)[0]))
        modddate = binascii.hexlify(moddate)
        debug_print("moddate %s (%s)" % (moddate, modtime))
        size = f.read(4)
        debug_print(
            "pysize %s (%d)" % (binascii.hexlify(size), struct.unpack("<L", size)[0])
        )
    code = marshal.load(f)
    f.close()
    return code


@not_rpython
def load_pyc_py2(fname):
    f = open(fname, "rb")
    magic = f.read(4)
    timestamp = f.read(4)
    code = marshal.load(f)
    f.close()
    return code


@not_rpython
def compile_py2(fname):
    f = create_file(fname)
    code = py.code.Source(f.read()).compile()
    f.close()
    return code


def rpy_load_py2(fname):
    f = create_file(fname)
    magic = f.read(4)
    timestamp = f.read(4)
    tc = f.read(1)
    pycode = unmarshal_pycode(f)
    f.close()
    return pycode


if __name__ == "__main__":
    import dis

    code = rpy_load_py2(sys.argv[1])
    dis.disassemble(code.co_code)
