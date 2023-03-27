    
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
    >>> M = o._diff_(u, s)
    >>> print(M)
    ['+2', '+3', '+4']
    >>> u = [1,2,3]
    >>> s = []
    >>> M = o._diff_(u, s)
    >>> print(M)
    ['-1', '-2', '-3']
    >>> r = [1,2,3]
    >>> l = [2,3,4]
    >>> M = o._diff_(r, l)
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


    >>> unset_holdings = o._read_num_file_('tests/t.set', 'unset', False)
    >>> o.write_master(path='tests/test_master.lst', del_list=unset_holdings, debug=False)
    >>> s,u,c = o.read_master(path='tests/test_master.lst', debug=False)
    >>> print(u)
    ['12345', '101112']
    >>> set_holdings = o._read_num_file_('tests/t.set', 'set', False)
    >>> o.write_master(path='tests/test_master.lst', add_list=set_holdings, debug=False)
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


    >>> o.write_master(path='tests/test_master.lst', add_list=set_holdings, del_list=unset_holdings, check_list=check_holdings, debug=False)
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
    >>> o._check_holdings_(test_check_records, configs, logger, False)
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
    >>> o._set_holdings_(test_add_records, configs, logger, False)
    +850939596 - success
    +850939592 - success
    operation 'set' total records: 2, 2 successful, and 0 errors


Test that MARC21 XML records can be loaded
------------------------------------------

>>> test_record_flat = """*** DOCUMENT BOUNDARY ***
... ... FORM=MARC
... .000. |aam a0n a
... .001. |aepl01318816
... .005. |a20140415031118.0
... .008. |a120510t20122011maua   j      000 1 eng c
... .010.   |a  2011277368
... .035.   |a(Sirsi) a1002054
... .035.   |a(Sirsi) a1002054
... .035.   |a(OCoLC)745979831
... .035.   |a(ULS) epl01318816
... .040.   |dUtOrBLW
... .082. 04|a[E]|223
... .099.   |aE DUD
... .100. 1 |aDuddle, Jonny.
... .245. 14|aThe pirates next door :|bstarring the Jolley-Rogers /|cJonny Duddle.
... .250.   |aFirst U.S. edition.
... .264.  1|aSomerville, Mass. :|bTemplar Books,|c2012.
... .264.  4|c©2011
... .300.   |a36 unnumbered pages :|bchiefly color illustrations ;|c26 x 30 cm
... .336.   |atext|2rdacontent
... .336.   |astill image|2rdacontent
... .337.   |aunmediated|2rdamedia
... .338.   |avolume|2rdacarrier
... .520.   |aWhen a pirate family moves into her quiet seaside town during ship
... repairs, young Matilda defies the edicts of the gossiping adults in the
... community to befriend young pirate Jim Lad.
... .596.   |a1 4 7 10 13 16 20 22
... .650.  0|aPirates|vJuvenile fiction.
... .650.  0|aFriendship|vJuvenile fiction.
... .650.  0|aNeighbors|vJuvenile fiction.
... .020.   |a0763658421
... .020.   |a9780763658427
... .947.   |fE-PR|hEPLZJBK|q9|p19.19
... .999.   |hEPLZJBK"""
