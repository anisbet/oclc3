    
Test oclc script's functionality.


>>> import oclc as o
>>> from log import Log
>>> from flat2marcxml import MarcXML


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
Diff report:
     total records: 3
        no changes: 0
           changes: 3
               (+): 3
               (-): 0
  over represented: 0.0%
 under represented: 100.0%
>>> print(M)
['+2', '+3', '+4']
>>> u = [1,2,3]
>>> s = []
>>> M = o.diff_deletes_adds(u, s)
Diff report:
     total records: 3
        no changes: 0
           changes: 3
               (+): 0
               (-): 3
  over represented: 100.0%
 under represented: 0.0%
>>> print(M)
['-1', '-2', '-3']
>>> r = [1,2,3]
>>> l = [2,3,4]
>>> M = o.diff_deletes_adds(r, l)
Diff report:
     total records: 4
        no changes: 2
           changes: 2
               (+): 1
               (-): 1
  over represented: 25.0%
 under represented: 25.0%
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
+(OCoLC) 123456
(OCoLC) 7777777
-(OCoLC) 123456
?999877
?(OCoLC) 88888888

>>> o._read_num_file_('tests/t.set', 'set', False)
['12345', '6789', '123456', '7777777']
>>> o._read_num_file_('tests/t.set', 'unset', False)
['12345', '101112', '7777777', '123456']
>>> o._read_num_file_('tests/t.set', 'check', False)
['12345', '7777777', '999877']


Check the writing and reading of the 'master.lst'
-----------


>>> unset_institution_holdings = o._read_num_file_('tests/t.set', 'unset', False)
>>> o.write_update_instruction_file(path='tests/test_master.lst', del_list=unset_institution_holdings, debug=False)
>>> s,u,c,d = o.read_master(path='tests/test_master.lst', debug=False)
>>> print(u)
['12345', '101112', '7777777', '123456']
>>> add_holdings = o._read_num_file_('tests/t.set', 'set', False)
>>> o.write_update_instruction_file(path='tests/test_master.lst', add_list=add_holdings, debug=False)
>>> s,u,c,d = o.read_master(path='tests/test_master.lst', debug=False)
>>> print(s)
['12345', '6789', '123456', '7777777']
>>> check_holdings = o._read_num_file_('tests/t.set', 'check', False)
>>> o.write_update_instruction_file(path='tests/test_master.lst', check_list=check_holdings, debug=False)
>>> s,u,c,d = o.read_master(path='tests/test_master.lst', debug=False)
>>> print(c)
['12345', '7777777', '999877']



Check for both set and unset
----------------------------


>>> o.write_update_instruction_file(path='tests/test_master.lst', add_list=add_holdings, del_list=unset_institution_holdings, check_list=check_holdings, debug=False)
>>> s,u,c,d = o.read_master(path='tests/test_master.lst', debug=False)
>>> print(f"{c}")
['12345', '7777777', '999877']
>>> print(f"{u}")
['12345', '101112', '7777777', '123456']
>>> print(f"{s}")
['12345', '6789', '123456', '7777777']
>>> master = ['-1234', '+1111', ' 2222', '?3333']
>>> o.write_update_instruction_file(path='tests/test_master.lst', master_list=master, debug=False)
>>> s,u,c,d = o.read_master(path='tests/test_master.lst', debug=False)
>>> print(f"{c}")
['3333']
>>> print(f"{u}")
['1234']
>>> print(f"{s}")
['1111']



Check that if you don't have any check requests an empty list is returned.
--------------------------------------------------------------------------


>>> check_list = ['-1234', '+1111', ' 2222', ' 3333']
>>> o.write_update_instruction_file(path='tests/test_master.lst', master_list=check_list, debug=False)
>>> s,u,c,d = o.read_master(path='tests/test_master.lst', debug=False)
>>> print(f"{c}")
[]

These tests have time stamps in them which never match the test conditions.
If you uncomment them you can see the results are similar ignoring timestamps.
# Send test OCLC numbers via the web service
# ------------------------------------------
# 
# >>> test_check_records = [
# ... 850939592,
# ... 850939596,
# ... 850939598,
# ... 850939600,
# ... 850939601,
# ... 850939602,
# ... 850940343,
# ... 850940351,
# ... 850940364,
# ... 850940368, ]
# >>> o.check_institutional_holdings(test_check_records, configs, logger, False)
# ?850939592 is OCPSB holding: True as of '2023-07-25 21:07:32'  OCLC number confirmed See http://worldcat.org/oclc/850939592 for more information.
# ?850939596 is OCPSB holding: True as of '2023-07-25 21:07:33'  OCLC number confirmed See http://worldcat.org/oclc/850939596 for more information.
# ?850939598 is OCPSB holding: False as of '2023-07-25 21:07:33' See http://worldcat.org/oclc/850939598 for more information.
# ?850939600 is OCPSB holding: True as of '2023-07-25 21:07:33'  OCLC number confirmed See http://worldcat.org/oclc/850939600 for more information.
# ?850939601 is OCPSB holding: False as of '2023-07-25 21:07:34' See http://worldcat.org/oclc/850939601 for more information.
# ?850939602 is OCPSB holding: True as of '2023-07-25 21:07:34'  OCLC number confirmed See http://worldcat.org/oclc/850939602 for more information.
# ?850940343 is OCPSB holding: False as of '2023-07-25 21:07:34' See http://worldcat.org/oclc/850940343 for more information.
# ?850940351 is OCPSB holding: False as of '2023-07-25 21:07:35' See http://worldcat.org/oclc/850940351 for more information.
# ?850940364 is OCPSB holding: False as of '2023-07-25 21:07:35' See http://worldcat.org/oclc/850940364 for more information.
# ?850940368 is OCPSB holding: False as of '2023-07-25 21:07:35' See http://worldcat.org/oclc/850940368 for more information.
# operation 'holdings' results.
#           succeeded: 10
#             warnings: 0
#               errors: 0
#       total records: 10
# ['850939592', '850939596', '850939598', '850939600', '850939601', '850939602', '850940343', '850940351', '850940364', '850940368']

# >>> test_add_records = [
# ... 850939596,
# ... 850939592,]
# >>> o.add_holdings(test_add_records, configs, logger, False)
# +850939592  added
# +850939596  added
# operation 'add / set' results.
#           succeeded: 2
#            warnings: 0
#              errors: 0
#       total records: 2

# Test deleting records
# >>> test_del_records = [
# ... 12345678,
# ... 1223334444,]
# >>> o.delete_holdings(test_del_records, configs, logger, False)
# -12345678  deleted
# -1223334444  deleted
# operation 'delete / unset' results.
#           succeeded: 2
#            warnings: 0
#              errors: 0
#       total records: 2


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
<record xmlns="http://www.loc.gov/MARC21/slim">
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




Test uploading MARC21 XML record
--------------------------------


>>> flat_record = [
... "*** DOCUMENT BOUNDARY ***",
... "FORM=MUSIC",
... ".000. |ajm a0c a",
... ".008. |a111222s2012    nyu||n|j|         | eng d",
... ".010.   |a   63011276 ",
... ".040.   |aOCWMS|beng|cOCPSB",
... ".100. 0 |aOCLC Developer Network",
... ".245. 10|aTest Record",
... ".500.   |aFOR OCLC DEVELOPER NETWORK DOCUMENTATION"]


Test write master
-----------------

>>> import oclc as o
>>> dels = [12345678,1223334444,]
>>> chks = [11111111,2222222222]
>>> adds = [22222222,2333333333,]
>>> dels = [33333333,4444444444,]
>>> done = [10000,20000,30000,40000]
>>> o.write_update_instruction_file(path='receipt_test.txt', add_list=adds, del_list=dels, check_list=chks, done_list=done)


>>> l = ['0','1','2','3',]
>>> USE_QUOTAS = True
>>> configs = {'checkQuota': 2}
>>> o.get_quota(l,'checkQuota',configs)
['0', '1']
>>> configs = {'checkQuota': -1}
>>> o.get_quota(l,'checkQuota',configs)
['0', '1', '2']
>>> configs = {'checkQuota': 1000}
>>> o.get_quota(l,'checkQuota',configs)
['0', '1', '2', '3']
>>> configs = {'wrongQuota': 5}
>>> o.get_quota(l,'checkQuota',configs)
['0', '1', '2', '3']
