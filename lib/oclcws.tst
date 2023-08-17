

Test specialized functions in the oclcws module

>>> from oclcws import OclcService
>>> from log import Logger
>>> import yaml
>>> logger = Logger('test.log')
>>> import sys
>>> from os.path import exists
>>> yaml_file = 'test.yaml'
>>> configs = {}
>>> if exists(yaml_file):
...     with open(yaml_file) as f:
...         try:
...             configs = yaml.safe_load(f)
...             client_id = configs['service']['clientId']
...             secret = configs['service']['secret']
...             inst_id = configs['service']['registryId']
...             inst_symbol = configs['service']['institutionalSymbol']
...         except yaml.YAMLError as exc:
...             sys.stderr.write(f"{exc}")
... else:
...     sys.stderr.write(f"*error, yaml file not found! Expected '{yaml_file}'")
...     sys.exit()

Test the list to parameter string.
---------------------------------


>>> L1 = [1,2,3]
>>> ws = OclcService(configs, logger=logger)
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

>>> oclc = OclcService(configs, logger=logger)
>>> oclc._is_expired_("2023-01-31 20:59:39Z")
True
>>> oclc._is_expired_("2050-01-31 00:59:39Z")
False
