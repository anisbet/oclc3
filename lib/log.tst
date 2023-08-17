    
Test if the following messages are written to the log file.

    >>> from log import Logger

Test logit
----------

    >>> log = Logger('test.log')
    >>> log.logit("Hello World!", include_timestamp=False)
    Hello World!
    >>> msgs = ["Hello ", "World!"]
    >>> log.logem(msgs, include_timestamp=False)
    Hello 
    World!
    