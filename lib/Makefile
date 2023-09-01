.PHONY: test

test: ../test.yaml
	-rm test.log 
	python oclcreport.py 
	python oclcws.py 
	# python listutils.py
	python flat2marcxml.py
	python flat.py