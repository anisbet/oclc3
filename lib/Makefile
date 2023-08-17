.PHONY: test

test: ../test.yaml
	-rm test.log
	python log.py 
	python oclcreport.py 
	python oclcws.py 
	python oclcrpt.py 
	python flat2marcxml.py