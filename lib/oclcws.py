###############################################################################
#
#
#
###############################################################################
import time
import datetime
import base64

# TODO: Manage authentication.
# TODO: * Determine if a given token has expired.
# TODO: * Store authorization response for reuse, and refresh the token if expired.
class OclcService:

    def __init__(self):
        pass

    # Determines if an expiry time has passed.
    # Param: Time in "%Y-%m-%d %H:%M:%SZ" format as it is stored in the authorization JSON
    #   returned from the OCLC web service authorize request.
    # Return: True if the token expires_at time has passed and False otherwise.
    def _is_expired_(self, expires_at:str):
        """
        >>> oclc = OclcService()
        >>> oclc._is_expired_("2023-01-31 20:59:39Z")
        True
        >>> oclc._is_expired_("2050-01-31 00:59:39Z")
        False
        """
        # token expiry time
        assert expires_at != None
        assert len(expires_at) == 20
        expiry_time = expires_at
        # parse the expiry time string into a datetime object
        expiry_datetime = datetime.datetime.strptime(expiry_time, "%Y-%m-%d %H:%M:%SZ")
        # get the current time as utc
        current_time = datetime.datetime.utcnow()
        # compare the current time to the expiry time
        if current_time > expiry_datetime:
            return True
        else:
            return False

    # Given a list of OCLC numbers make sure they are strings and not ints, then 
    # concatenate them into the maximum number of oclc numbers that the service 
    # permits in one call. See parameter count for more information.
    # Param:  list of OCLC numbers or strings of numbers.
    # Param:  Optional integer of the max number of OCLC numbers allowed as URL
    #   parameters to the web service call. Default 50.
    def _oclc_numbers_(self, numbers:list, max:int = 50):
        """
        >>> L1 = [1,2,3]
        >>> service = OclcService()
        >>> service._oclc_numbers_(L1)
        '1,2,3'
        >>> L1 = ['1','2','3']
        >>> service._oclc_numbers_(L1)
        '1,2,3'
        >>> L1 = ["1","2","3"]
        >>> service._oclc_numbers_(L1)
        '1,2,3'
        """
        assert isinstance(numbers, list)
        assert isinstance(max, int)
        param_list = []
        count = 0
        while len(numbers) > 0 and count <= max:
            n = numbers.pop(0)
            param_list.append(f"{n}")
            count += 1
        return ','.join(param_list)
    
    # TODO: Manage authorization to the OCLC web service.
    def _authorize_(self, clientId:str, secret:str):
        pass


if __name__ == "__main__":
    import doctest
    doctest.testmod()