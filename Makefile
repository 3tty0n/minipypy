RPYTHON = ./pypy/rpython/bin/rpython
PYTHONPATH=.:./pypy

compile:
	PYTHONPATH=$(PYTHONPATH) $(RPYTHON) -O2 minipypy/main.py

compile-jit:
	PYTHONPATH=$(PYTHONPATH) $(RPYTHON) -Ojit minipypy/main.py

compile-byte:
	python2 -m compileall tests/
