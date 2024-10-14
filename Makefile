RPYTHON = ./pypy/rpython/bin/rpython

compile:
	$(RPYTHON) -O2 minipypy/main.py

compile-jit:
	$(RPYTHON) -Ojit minipypy/main.py
