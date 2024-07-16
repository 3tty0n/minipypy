import binascii
import marshal
import struct
import sys
import time


def load_pyc(fname):
    f = open(fname, "rb")
    magic = f.read(4)
    # print("magic %s" % (binascii.hexlify(magic)))
    read_date_and_size = True
    flags = struct.unpack("<L", f.read(4))[0]
    hash_based = bool(flags & 0x01)
    check_source = bool(flags & 0x02)
    # print(f"flags {flags:#08x}")
    if hash_based:
        source_hash = f.read(8)
        read_date_and_size = False
        # print(f"hash {binascii.hexlify(source_hash)}")
        # print(f"check_source {check_source}")
    if read_date_and_size:
        moddate = f.read(4)
        modtime = time.asctime(time.localtime(struct.unpack("<L", moddate)[0]))
        # print(f"moddate {binascii.hexlify(moddate)} ({modtime})")
        size = f.read(4)
        # print("pysize %s (%d)" % (binascii.hexlify(size), struct.unpack("<L", size)[0]))
    code = marshal.load(f)
    f.close()
    return code


if __name__ == "__main__":
    import opcode

    code = load_pyc(sys.argv[1])
    import pdb

    breakpoint()
