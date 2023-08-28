from datetime import datetime
import sys

# Basic logger.
class Logger:
    
    def __init__(self, log_file:str, debug:bool=False):
        self.log = log_file
        self.debug = debug
        self.date_format = '%Y-%m-%d %H:%M:%S'

    # Logs entries with timestamps.
    # param: message str to write to log. 
    # param: level string values can be 'error', 'info'. Default 'info'.
    # return: the time-stamped, formatted error message as was written to the log.
    def logit(self, message:str, level:str='info', include_timestamp:bool=False):
        time_str = ''
        if include_timestamp:
            time_str = f"[{datetime.now().strftime(self.date_format)}] "
        if level == 'error':
            msg = f"{time_str}*error, {message}"
            sys.stderr.write(f"{msg}\n")
        else:
            msg = f"{time_str}{message}"
            sys.stdout.write(f"{msg}\n")
        with open(self.log, encoding='ISO-8859-1', mode='a') as log:
            log.write(f"{msg}\n")
        log.close()

    # Logs multiple results. 
    # param: list of message strings. 
    # param: level string level of reporting either 'error', 'info'. Default 'info'.
    # return: List of logged strings.
    def logem(self, messages:list, level:str='info', include_timestamp:bool=False):
        time_str = ''
        if include_timestamp:
            time_str = f"[{datetime.now().strftime(self.date_format)}] "
        with open(self.log, encoding='ISO-8859-1', mode='a') as log:
            if level == 'error':
                for message in messages:
                    msg = f"{time_str}*error, {message}"
                    log.write(f"{msg}\n")
                    sys.stderr.write(f"{msg}\n")
            else:
                for message in messages:
                    msg = f"{time_str}{message}"
                    log.write(f"{msg}\n")
                    sys.stdout.write(f"{msg}\n")
        log.close()

    def get_log_file(self):
        return self.log

if __name__ == "__main__":
    import doctest
    doctest.testfile("clog.tst")