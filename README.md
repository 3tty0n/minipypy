# minipypy

This is minipypy, a subset of the PyPy interpreter. This project was created to experiment with implementing a new compilation technique, optimizations, and so on.

For the sake of simplicity, minipypy borrows Python's bytecode compiler. It loads a compiled bytecode by CPython/PyPy and interprets it.

## Prerequisite

- PyPy and RPython 2.7
  - Due to compile minipypy by RPython

## Future Work

### Python 3 Support

- [ ] Support `marshal.load` for Python 3
