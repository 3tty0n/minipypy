RPYTHON = ./pypy/rpython/bin/rpython
PYTHONPATH=.:./pypy

compile:
	PYTHONPATH=$(PYTHONPATH) $(RPYTHON) -O2 minipypy/main.py

compile-jit:
	PYTHONPATH=$(PYTHONPATH) $(RPYTHON) -Ojit minipypy/main.py

compile-byte:
	$(eval SRC := $(shell find ./tests -name "*.py" -type f))
	@for pyc in $(SRC); do echo $$pyc; python2 -m py_compile $$pyc; done

clean-byte:
	$(RM) tests/*.pyc
