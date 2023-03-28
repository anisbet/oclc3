    
Test oclc script's functionality.


    >>> import oclc as o
    >>> from lib.log import Log
    >>> configs = o._load_yaml_('test.yaml')
    >>> logger = Log(configs['report'])

Setting
-------


    >>> o._find_set_('12345.012 is the number you are looking for')
    >>> o._find_set_('12345')
    '12345'
    >>> o._find_set_('-12345')
    >>> o._find_set_('+12345')
    '12345'
    >>> o._find_set_(' 12345')
    >>> o._find_set_('12345 is the number you are looking for')
    '12345'


Unsetting
---------


    >>> o._find_unset_('12345.012 is the number you are looking for')
    >>> o._find_unset_('12345')
    '12345'
    >>> o._find_unset_('+12345')
    >>> o._find_unset_('-12345')
    '12345'
    >>> o._find_unset_(' 12345')
    >>> o._find_unset_('12345 is the number you are looking for')
    '12345'


Checking
-------


    >>> o._find_check_('12345.012 is the number you are looking for')
    >>> o._find_check_('?12345')
    '12345'
    >>> o._find_check_('-12345')
    >>> o._find_check_('?12345')
    '12345'
    >>> o._find_check_(' 12345')
    >>> o._find_check_('12345 is the number you are looking for')
    '12345'


Diff-ing two different Lists
----------------------------


    >>> u = []
    >>> s = [2,3,4]
    >>> M = o.diff_deletes_adds(u, s)
    >>> print(M)
    ['+2', '+3', '+4']
    >>> u = [1,2,3]
    >>> s = []
    >>> M = o.diff_deletes_adds(u, s)
    >>> print(M)
    ['-1', '-2', '-3']
    >>> r = [1,2,3]
    >>> l = [2,3,4]
    >>> M = o.diff_deletes_adds(r, l)
    >>> print(M)
    ['-1', ' 2', ' 3', '+4']

Test if the following strings parse integer OCLC numbers correctly when 
desired operation is unset.

    >>> import oclc as o


Reading a oclc number list file.
-------


Given file 't.set' contains the following values:

12345
+6789
 99999
 2990
-101112
?999877

    >>> o._read_num_file_('tests/t.set', 'set', False)
    ['12345', '6789']
    >>> o._read_num_file_('tests/t.set', 'unset', False)
    ['12345', '101112']
    >>> o._read_num_file_('tests/t.set', 'check', False)
    ['12345', '999877']


Check the writing and reading of the 'master.lst'
-----------


    >>> unset_institution_holdings = o._read_num_file_('tests/t.set', 'unset', False)
    >>> o.write_master(path='tests/test_master.lst', del_list=unset_institution_holdings, debug=False)
    >>> s,u,c = o.read_master(path='tests/test_master.lst', debug=False)
    >>> print(u)
    ['12345', '101112']
    >>> set_institution_holdings = o._read_num_file_('tests/t.set', 'set', False)
    >>> o.write_master(path='tests/test_master.lst', add_list=set_institution_holdings, debug=False)
    >>> s,u,c = o.read_master(path='tests/test_master.lst', debug=False)
    >>> print(s)
    ['12345', '6789']
    >>> check_holdings = o._read_num_file_('tests/t.set', 'check', False)
    >>> o.write_master(path='tests/test_master.lst', check_list=check_holdings, debug=False)
    >>> s,u,c = o.read_master(path='tests/test_master.lst', debug=False)
    >>> print(c)
    ['12345', '999877']



Check for both set and unset
----------------------------


    >>> o.write_master(path='tests/test_master.lst', add_list=set_institution_holdings, del_list=unset_institution_holdings, check_list=check_holdings, debug=False)
    >>> s,u,c = o.read_master(path='tests/test_master.lst', debug=False)
    >>> print(f"{c}")
    ['12345', '999877']
    >>> print(f"{u}")
    ['12345', '101112']
    >>> print(f"{s}")
    ['12345', '6789']
    >>> master = ['-1234', '+1111', ' 2222', '?3333']
    >>> o.write_master(path='tests/test_master.lst', master_list=master, debug=False)
    >>> s,u,c = o.read_master(path='tests/test_master.lst', debug=False)
    >>> print(f"{c}")
    ['3333']
    >>> print(f"{u}")
    ['1234']
    >>> print(f"{s}")
    ['1111']



Check that if you don't have any check requests an empty list is returned.
--------------------------------------------------------------------------


    >>> check_list = ['-1234', '+1111', ' 2222', ' 3333']
    >>> o.write_master(path='tests/test_master.lst', master_list=check_list, debug=False)
    >>> s,u,c = o.read_master(path='tests/test_master.lst', debug=False)
    >>> print(f"{c}")
    []


Send test OCLC numbers via the web service
------------------------------------------

    >>> test_check_records = [
    ... 850939592,
    ... 850939596,
    ... 850939598,
    ... 850939600,
    ... 850939601,
    ... 850939602,
    ... 850940343,
    ... 850940351,
    ... 850940364,
    ... 850940368, ]
    >>> o.check_holdings(test_check_records, configs, logger, False)
    ?850939592 - success
    ?850939596 - success
    ?850939598 - success
    ?850939600 - success
    ?850939601 - success
    ?850939602 - success
    ?850940343 - success
    ?850940351 - success
    ?850940364 - success
    ?850940368 - success
    operation 'check' total records: 10, 10 successful, 0 warnings, and 0 errors

    >>> test_add_records = [
    ... 850939592,
    ... 850939596,]
    >>> o.set_institution_holdings(test_add_records, configs, logger, False)
    +850939592 - success
    +850939596 - success
    operation 'set' total records: 2, 2 successful, and 0 errors


Test that MARC21 XML records can be loaded
------------------------------------------

>>> marc_slim = MarcXML([
... "*** DOCUMENT BOUNDARY ***",
... "FORM=MUSIC",
... ".000. |ajm a0c a",
... ".001. |aocn769144454",
... ".003. |aOCoLC",
... ".005. |a20140415031111.0",
... ".007. |asd fsngnnmmned",
... ".008. |a111222s2012    nyu||n|j|         | eng d",
... ".024. 1 |a886979578425",
... ".028. 00|a88697957842",
... ".035.   |a(Sirsi) a1001499",
... ".035.   |a(Sirsi) a1001499",
... ".035.   |a(OCoLC)769144454",
... ".035.   |a(CaAE) a1001499",
... ".040.   |aTEFMT|cTEFMT|dTEF|dBKX|dEHH|dNYP|dUtOrBLW"])
>>> print(marc_slim)
<?xml version="1.0" encoding="UTF-8"?>
<record xmlns="http://www.loc.gov/MARC21/slim" >
<leader>jm a0c a</leader>
<controlfield tag="001">ocn769144454</controlfield>
<controlfield tag="003">OCoLC</controlfield>
<controlfield tag="005">20140415031111.0</controlfield>
<controlfield tag="007">sd fsngnnmmned</controlfield>
<controlfield tag="008">111222s2012    nyu||n|j|         | eng d</controlfield>
<datafield tag="024" ind1="1" ind2=" ">
	<subfield code="a">886979578425</subfield>
</datafield>
<datafield tag="028" ind1="0" ind2="0">
	<subfield code="a">88697957842</subfield>
</datafield>
<datafield tag="035" ind1=" " ind2=" ">
	<subfield code="a">(Sirsi) a1001499</subfield>
</datafield>
<datafield tag="035" ind1=" " ind2=" ">
	<subfield code="a">(Sirsi) a1001499</subfield>
</datafield>
<datafield tag="035" ind1=" " ind2=" ">
	<subfield code="a">(OCoLC)769144454</subfield>
</datafield>
<datafield tag="035" ind1=" " ind2=" ">
	<subfield code="a">(CaAE) a1001499</subfield>
</datafield>
<datafield tag="040" ind1=" " ind2=" ">
	<subfield code="a">TEFMT</subfield>
	<subfield code="c">TEFMT</subfield>
	<subfield code="d">TEF</subfield>
	<subfield code="d">BKX</subfield>
	<subfield code="d">EHH</subfield>
	<subfield code="d">NYP</subfield>
	<subfield code="d">UtOrBLW</subfield>
</datafield>
</record>

