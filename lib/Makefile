.PHONY: test

test: ../test.yaml
	-rm test.log
	python clog.py 
	python oclcreport.py 
	python oclcws.py 
	python listutils.py
	python flat2marcxml.py