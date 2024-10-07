#!/usr/bin/env python2
import argparse
import dis
import marshal

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="compile")
    parser.add_argument("filename")
    args = parser.parse_args()
    f = open(args.filename, "rb")
    f.read(4)
    f.read(4)
    code = marshal.load(f)
    dis.dis(code)
    import pdb

    pdb.set_trace()
