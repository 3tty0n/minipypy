#!/usr/bin/env python
import argparse
import py_compile

def compile_file(path):
    "generate .pyc file"
    py_compile.compile(path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='compile')
    parser.add_argument('filename')

    args = parser.parse_args()
    compile_file(args.filename)
