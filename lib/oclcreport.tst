
Tests for web service responses, but also provides reporting.
# Spec for Results
* Report how long the script ran.
* Report total hits and breakdown by operation.
* Checks should report the original sent and value returned by OCLC and if an update is required. Updating this information could be in a report that could be made available to CMA for record updating, but automating is out of scope for now.
* Adds and delete counts shall be reported along with any errors.
* The master list (receipt) shall be updated with what happened with either of the following.
  * ` - success` if everything went as planned.
  * ` - error [reason]`, on error output the error.
  * ` - pending` if the web service hit count exceeded quota
  * ` - warning: old=[old] new=[new]` if the two numbers differ, and ` - success` if no change required.

	>>> from oclcreport import OclcReport
	>>> import json
	>>> from log import Log
    >>> logger = Log('test.log')

	>>> DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

	>>> check_response = json.loads("""{
	... "entries": [{
	...     "title": "12345",
	...     "content": {
	...       "requestedOclcNumber": "12345",
	...       "currentOclcNumber": "12345",
	...       "institution": "OCPSB",
	...       "status": "HTTP 200 OK",
	...       "detail": "Record found.",
	...       "id": "http://worldcat.org/oclc/12345",
	...       "found": true,
	...       "merged": false
	...     },
	...     "updated": "2023-03-21T23:17:51.678Z"
	...   },
	...   {
	...     "title": "67890",
	...     "content": {
	...       "requestedOclcNumber": "67890",
	...       "currentOclcNumber": "6777790",
	...       "institution": "OCPSB",
	...       "status": "HTTP 200 OK",
	...       "detail": "Record found.",
	...       "id": "http://worldcat.org/oclc/67890",
	...       "found": true,
	...       "merged": false
	...     },
	...     "updated": "2023-03-21T23:17:51.679Z"
	...   },
	...   {
	...     "title": "999999999",
	...     "content": {
	...       "requestedOclcNumber": "999999999",
	...       "currentOclcNumber": "999999999",
	...       "institution": "OCPSB",
	...       "status": "HTTP 404 Not Found",
	...       "detail": "Record not found.",
	...       "id": "http://worldcat.org/oclc/999999999",
	...       "found": false,
	...       "merged": false
	...     },
	...     "updated": "2023-03-21T23:17:51.679Z"
	...   }
	... ],
	... "extensions": [{
	...     "name": "os:totalResults",
	...     "attributes": {
	...       "xmlns:os": "http://a9.com/-/spec/opensearch/1.1/"
	...     },
	...     "children": [
	...       "3"
	...     ]
	...   },
	...   {
	...     "name": "os:startIndex",
	...     "attributes": {
	...       "xmlns:os": "http://a9.com/-/spec/opensearch/1.1/"
	...     },
	...     "children": [
	...       "1"
	...     ]
	...   },
	...   {
	...     "name": "os:itemsPerPage",
	...     "attributes": {
	...       "xmlns:os": "http://a9.com/-/spec/opensearch/1.1/"
	...     },
	...     "children": [
	...       "3"
	...     ]
	...   }
	... ]
	... }""")
	>>> report = OclcReport(logger=logger)
	>>> report.check_response(check_response)
	['?12345 - success', '?67890 - updated to 6777790', '?999999999 - error Record not found.']
	


Test the checks dictionary for tallies
--------------------------------------

	>>> report.get_check_results()
	{'total': 3, 'success': 2, 'errors': 1}

