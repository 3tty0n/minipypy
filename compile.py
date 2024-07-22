#!/usr/bin/env python2
import argparse
import dis
import marshal
import py_compile

def compile_file(path):
    "generate .pyc file"
    py_compile.compile(path)

def compile_py2(path):
    f = open(args.filename, 'r')
    code = compile(f.read(), '', 'exec')
    f.close()

    nameout = args.filename.strip('.py') + '.pyc'
    fout = open(nameout, 'wb')
    fout.write(b'0000') # dummy value for magic number
    fout.write(b'0000') # dummy value for timestamp
    marshal.dump(code, fout)

    fout.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='compile')
    parser.add_argument('filename')
    args = parser.parse_args()
    compile_py2(args.filename)
