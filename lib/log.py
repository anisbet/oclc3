from datetime import datetime

# Basic logger.
class Log:
    
    def __init__(self, file:str):
        self.log = file
        self.date_format = '%Y-%m-%d %H:%M:%S'

    # Logs entries with timestamps.
    # param: message str to write to log. 
    # param: level string values can be 'error', 'info'. Default 'info'.
    # return: the time-stamped, formatted error message as was written to the log.
    def logit(self, message:str, level:str='info') -> str:
        time_str = datetime.now().strftime(self.date_format)
        if level == 'error':
            msg = f"[{time_str}] *error, {message}"
        else:
            msg = f"[{time_str}] {message}"
        with open(self.log, encoding='utf-8', mode='a') as log:
            log.write(f"{msg}\n")
        log.close()
        return msg

    # Logs multiple results. 
    # param: list of message strings. 
    # param: level string level of reporting either 'error', 'info'. Default 'info'.
    # return: List of logged strings.
    def logem(self, messages:list, level:str='info') ->list:
        time_str = datetime.now().strftime(self.date_format)
        ret_list = []
        with open(self.log, encoding='utf-8', mode='a') as log:
            if level == 'error':
                for message in messages:
                    log.write(f"[{time_str}] *error, {message}\n")
                    ret_list.append(f"[{time_str}] *error, {message}")
            else:
                for message in messages:
                    log.write(f"[{time_str}] {message}\n")
                    ret_list.append(f"[{time_str}] {message}")
        log.close()
        return ret_list

    # Logs entries as errors with timestamps. 
    # param: message str.
    # return: str of error massage with timestamp.
    def logerr(self, message:str) -> str:
        return self.logit(message, level='error')

if __name__ == "__main__":
    import doctest
    doctest.testfile("../tests/log.tst")