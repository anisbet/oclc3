.PHONY: test

test: test.yaml
	-rm test.log
	# make -C lib
	python oclc.py 