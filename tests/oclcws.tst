

Test specialized functions in the oclcws module

    >>> from oclcws import OclcService


Test the list to parameter string.
---------------------------------


    >>> L1 = [1,2,3]
    >>> ws = OclcService('test.yaml')
    >>> ws._list_to_param_str_(L1)
    '1,2,3'
    >>> L1 = ['1','2','3']
    >>> ws._list_to_param_str_(L1)
    '1,2,3'
    >>> L1 = ["1","2","3"]
    >>> ws._list_to_param_str_(L1)
    '1,2,3'



Test if token is expired
------------------------

    >>> oclc = OclcService('test.yaml')
    >>> oclc._is_expired_("2023-01-31 20:59:39Z")
    True
    >>> oclc._is_expired_("2050-01-31 00:59:39Z")
    False
