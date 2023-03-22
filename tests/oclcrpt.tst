Test a database used to store the OCLC search results
-----------------------------------------------------

    >>> from oclcrpt import OclcRpt
    >>> import json

Tests database create table
---------------------------


    >>> o = OclcRpt('test.yaml', True)
    >>> cols = ['a','b','c']
    >>> o._create_table_('test', cols)
    create query: CREATE TABLE IF NOT EXISTS test (
        a TEXT,
        b TEXT,
        c TEXT
    )


Test that you can store 'set' request JSON
------------------------------------------


    >>> d=json.loads("""
    ... {"entries":[
    ... {"title":"850939592","content":
    ... {"requestedOclcNumber":"850939592","currentOclcNumber":"850939592",
    ...  "institution":"OCPSB","status":"HTTP 200 OK",
    ...  "detail":"Record found.","id":"http://worldcat.org/oclc/850939592",
    ...  "found":true,
    ...  "merged":false},
    ... "updated":"2023-01-31T20:39:40.088Z"},
    ... {"title":"850939596",
    ...  "content":{"requestedOclcNumber":"850939596","currentOclcNumber":"850939596",
    ...  "institution":"OCPSB","status":"HTTP 200 OK","detail":"Record found.",
    ...  "id":"http://worldcat.org/oclc/850939596",
    ...  "found":true,
    ...  "merged":false},
    ... "updated":"2023-01-31T20:39:40.089Z"}
    ... ]}""")
    >>> o = OclcRpt('test.yaml', True)
    >>> o.set_and_check_reponse(d)
    create query: CREATE TABLE IF NOT EXISTS added (
        title TEXT,
        requestedOclcNumber TEXT,
        currentOclcNumber TEXT,
        institution TEXT,
        status TEXT,
        detail TEXT,
        id TEXT,
        found TEXT,
        merged TEXT,
        updated TEXT
    )
    loaded 2 records.
    2