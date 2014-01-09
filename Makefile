all:
	@/usr/bin/env python2 setup.py sdist
	
python3:
	@/usr/bin/env python3 setup.py sdist

.PHONY: all
