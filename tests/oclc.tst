    
Test if the following strings parse integer OCLC numbers correctly when 
desired operation is unset.
    >>> import oclc as o

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