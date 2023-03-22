    
Test if the following messages are written to the log file.

    >>> from log import Log
    >>> from datetime import datetime
    >>> DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

Test logit
----------

    >>> log = Log('test.log')
    >>> msg = f"[{datetime.now().strftime(DATE_FORMAT)}] Hello World!"
    >>> if log.logit("Hello World!") == msg:
    ...   print(True)
    ... else:
    ...   print(False)
    True
    >>> msg = f"[{datetime.now().strftime(DATE_FORMAT)}] *error, Hello World!"
    >>> if log.logerr("Hello World!") == msg:
    ...   print(True)
    ... else:
    ...   print(False)
    True
    >>> expected = [f"[{datetime.now().strftime(DATE_FORMAT)}] Hello ", f"[{datetime.now().strftime(DATE_FORMAT)}] World!"]
    >>> msgs = ["Hello ", "World!"]
    >>> result = log.logem(msgs)
    >>> for i in range(len(result)):
    ...     if result[i] == expected[i]:
    ...         print(True)
    ...     else:
    ...         print(False)
    True
    True