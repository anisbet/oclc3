###############################################################################
#
# Purpose: Provide wrappers for WorldCat Metadata API.
# Date:    Tue Jan 31 15:48:12 EST 2023
# Copyright 2023 Andrew Nisbet
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###############################################################################
import datetime
import base64
import requests
import json
import os

TOKEN_CACHE = '_auth_.json'
# TODO: Manage authentication.
class OclcService:

    # Possible useful arguments to the constructor.
    # clientId:str='some_id'
    # secret:str='s3cR3t'
    # registryId:str='128807'
    # institutionalSymbol:str='CNEDM'
    # debug:bool=False
    def __init__(self, configs:dict = {}):
        self.client_id = ''
        self.secret = ''
        self.inst_id = ''
        self.inst_symbol = ''
        self.auth_json = ''
        try:
            self.client_id   = configs.get('clientId')
            self.secret      = configs.get('secret')
            self.inst_id     = configs.get('registryId')
            self.inst_symbol = configs.get('institutionalSymbol')
            self.debug       = configs.get('debug')
        except KeyError:
            pass # They will get set somewhere else or we are testing.
        if len(self.client_id) > 0 and len(self.secret) > 0:
            self.auth_json = self._authenticate_worldcat_metadata_()
        # If successful the self.auth_json object will contain the following.
        # {
        # 'access_token': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 
        # 'expires_at': '2023-01-31 20:17:26Z', 
        # 'authenticating_institution_id': '128807', 
        # 'principalID': '', 
        # 'context_institution_id': '128807', 
        # 'scopes': 'WorldCatMetadataAPI:manage_bibs WorldCatMetadataAPI:view_brief_bib WorldCatMetadataAPI:view_retained_holdings WorldCatMetadataAPI:manage_institution_lhrs WorldCatMetadataAPI:manage_institution_holdings WorldCatMetadataAPI:view_summary_holdings WorldCatMetadataAPI:view_my_holdings WorldCatMetadataAPI:manage_institution_lbds', 
        # 'token_type': 'bearer', 
        # 'expires_in': 1199, 
        # 'principalIDNS': ''
        # }

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
    def _list_to_param_str_(self, numbers:list, max:int = 50):
        """
        >>> L1 = [1,2,3]
        >>> service = OclcService()
        >>> service._list_to_param_str_(L1)
        '1,2,3'
        >>> L1 = ['1','2','3']
        >>> service._list_to_param_str_(L1)
        '1,2,3'
        >>> L1 = ["1","2","3"]
        >>> service._list_to_param_str_(L1)
        '1,2,3'
        """
        param_list = []
        count = 0
        while len(numbers) > 0 and count < max:
            n = numbers.pop(0)
            # Don't add empty or Null values.
            if n == '' or n == None:
                continue
            param_list.append(f"{n}")
            count += 1
        return ','.join(param_list)
    
    # Manage authorization to the OCLC web service.
    def _authenticate_worldcat_metadata_(self):
        encoded_auth = base64.b64encode(f"{self.client_id}:{self.secret}".encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        url = "https://oauth.oclc.org/token?grant_type=client_credentials&scope=WorldCatMetadataAPI"
        response = requests.post(url, headers=headers)
        if self.debug == True:
            print(f"{response.json()}")
        self.auth_json = response.json()
        # {
        # 'access_token': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 
        # 'expires_at': '2023-01-31 20:17:26Z', 
        # 'authenticating_institution_id': '128807', 
        # 'principalID': '', 
        # 'context_institution_id': '128807', 
        # 'scopes': 'WorldCatMetadataAPI:manage_bibs WorldCatMetadataAPI:view_brief_bib WorldCatMetadataAPI:view_retained_holdings WorldCatMetadataAPI:manage_institution_lhrs WorldCatMetadataAPI:manage_institution_holdings WorldCatMetadataAPI:view_summary_holdings WorldCatMetadataAPI:view_my_holdings WorldCatMetadataAPI:manage_institution_lbds', 
        # 'token_type': 'bearer', 
        # 'expires_in': 1199, 
        # 'principalIDNS': ''
        # }

    # Tests and refreshes authentication token.
    def _get_access_token_(self):
        expiry_deadline = '1900-01-01 00:00:00Z'
        if os.path.isfile(TOKEN_CACHE):
            print(f"attempting to use cached auth.")
            with open(TOKEN_CACHE, 'r') as f:
                self.auth_json = json.load(f)
            f.close()
        try:
            expiry_deadline = self.auth_json['expires_at']
            if self._is_expired_(expiry_deadline) == True:
                self._authenticate_worldcat_metadata_()
                if self.debug == True:
                    print(f"refreshed auth token, expiry: {expiry_deadline}")
            else:
                if self.debug == True:
                    print(f"auth token is valid until {expiry_deadline}") 
        except KeyError:
            self._authenticate_worldcat_metadata_()
            if self.debug == True:
                print(f"getting new auth token, expiry: {expiry_deadline}")
        except TypeError:
            self._authenticate_worldcat_metadata_()
            if self.debug == True:
                print(f"getting new auth token, expiry: {expiry_deadline}")
        # Cache the results for repeated testing.
        with open(TOKEN_CACHE, 'w', encoding='utf-8') as f:
            # Use json.dump for streams files, or sockets and dumps for formatted strings.
            json.dump(self.auth_json, f, ensure_ascii=False, indent=2)
        return self.auth_json['access_token']

    # Takes a list of OCLC numbers as integers, and removes the max allowed count for 
    # verification at OCLC. The remainder of the list and the JSON response is returned.
    # Param:  List of OCLC numbers (as integers) to verify.
    # Return: List of two elements L[0]=List of remaining OCLC numbers, L[1]=response JSON.
    def get_holdings(self, oclcNumbers:list):
        access_token = self._get_access_token_()
        headers = {
            "accept": "application/atom+json",
            "Authorization": f"Bearer {access_token}"
        }
        # curl -X 'POST' \
        #   'https://worldcat.org/ih/datalist?oclcNumbers=850939592,850939596&inst=128807&instSymbol=OCPSB' \
        #   -H 'accept: application/atom+json' \
        #   -H 'Authorization: Bearer xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        oclc_nums_str = self._list_to_param_str_(oclcNumbers)
        url = f"https://worldcat.org/bib/checkcontrolnumbers?oclcNumbers={oclc_nums_str}"
        response = requests.get(url, headers=headers)
        # print(f"response: '{response.json()}'")
        # {'entries': [
        #   {'title': '850939592', 
        #     'content': {
        #       'requestedOclcNumber': '850939592', 
        #       'currentOclcNumber': '850939592', 
        #       'institution': 'OCPSB', 'status': 'HTTP 200 OK', 'detail': 'Record found.', 
        #       'id': 'http://worldcat.org/oclc/850939592', 
        #       'found': True, 
        #       'merged': False
        #     }, 
        #     'updated': '2023-01-31T20:39:40.088Z'
        #   }, 
        #   {'title': '850939596', 
        #     'content': {
        #       'requestedOclcNumber': '850939596', 
        #       'currentOclcNumber': '850939596', 
        #       'institution': 'OCPSB', 'status': 'HTTP 200 OK', 'detail': 'Record found.', 
        #       'id': 'http://worldcat.org/oclc/850939596', 
        #       'found': True, 
        #       'merged': False
        #     }, 
        #     'updated': '2023-01-31T20:39:40.089Z'
        #  }]
        # }
        # return the list of remaining OCLC numbers and JSON results.
        return [oclcNumbers, response.json()]


    def delete_holdings(self, oclcNumbers:list, cascade:int = 1):
        # curl -X 'DELETE' \
        # 'https://worldcat.org/ih/datalist?oclcNumbers=1234567,2332344&cascade=1&inst=128807&instSymbol=OCPSB' \
        # -H 'accept: application/atom+json' \
        # -H 'Authorization: Bearer xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        ## cascade
        # Whether or not to execute the operation if a local holdings record, or local biblliographic record
        # exists. 0 - don't remove holdings if local holding record or local bibliographic record exists 
        # 1 - yes remove holdings and delete local holdings record or local bibliographic record exists.
        # Request URL
        # https://worldcat.org/ih/datalist?oclcNumbers=1234567,2332344&cascade=1&inst=128807&instSymbol=OCPSB
        pass

    def update_holdings(self, records:dict):
        pass

    def create_holdings(self, records:dict):
        # curl -X 'POST' \
        # 'https://worldcat.org/ih/datalist?oclcNumbers=777890&inst=128807&instSymbol=OCPSB' \
        # -H 'accept: application/atom+json' \
        # -H 'Authorization: Bearer xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' \
        # -d ''
        # https://worldcat.org/ih/datalist?oclcNumbers=777890&inst=128807&instSymbol=OCPSB
        pass

if __name__ == "__main__":
    import doctest
    doctest.testmod()