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
from os.path import dirname, join, exists
import sys
from lib.log import Log

TOKEN_CACHE = '_auth_.json'

class OclcService:

    # Reads the yaml file for necessary configs.
    def __init__(self, configs:dict, logger:Log, debug:bool=False):
        
        self.configs     = configs
        self.client_id   = configs['service']['clientId']
        self.secret      = configs['service']['secret']
        self.inst_id     = configs['service']['registryId']
        self.inst_symbol = configs['service']['institutionalSymbol']
        self.logger      = logger
        self.debug       = debug
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
    def _is_expired_(self, expires_at:str) -> bool:
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
    #   parameters to the web service call. Default 50, the limit specified by
    #   OCLC for most calls that take batches of numbers.
    def _list_to_param_str_(self, numbers:list, max:int = 50) -> str:
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
            self.logger.logit(f"{response.json()}")
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
    def _get_access_token_(self) -> str:
        expiry_deadline = '1900-01-01 00:00:00Z'
        if exists(TOKEN_CACHE):
            with open(TOKEN_CACHE, 'r') as f:
                self.auth_json = json.load(f)
            f.close()
        try:
            expiry_deadline = self.auth_json['expires_at']
            if self._is_expired_(expiry_deadline) == True:
                self._authenticate_worldcat_metadata_()
                if self.debug == True:
                    self.logger.logit(f"refreshed auth token, expiry: {expiry_deadline}")
            else:
                if self.debug == True:
                    self.logger.logit(f"auth token is valid until {expiry_deadline}") 
        except KeyError:
            self._authenticate_worldcat_metadata_()
            if self.debug == True:
                self.logger.logit(f"getting new auth token, expiry: {expiry_deadline}")
        except TypeError:
            self._authenticate_worldcat_metadata_()
            if self.debug == True:
                self.logger.logit(f"getting new auth token, expiry: {expiry_deadline}")
        # Cache the results for repeated testing.
        with open(TOKEN_CACHE, 'w', encoding='utf-8') as f:
            # Use json.dump for streams files, or sockets and dumps for formatted strings.
            json.dump(self.auth_json, f, ensure_ascii=False, indent=2)
        return self.auth_json['access_token']

    # Takes a list of OCLC numbers as integers, and removes the max allowed count for 
    # verification at OCLC. The remainder of the list and the JSON response is returned.
    # Param:  List of OCLC numbers (as integers) to verify.
    # Return: response JSON.
    def check_control_numbers(self, oclc_numbers:list) -> dict:
        access_token = self._get_access_token_()
        headers = {
            "accept": "application/atom+json",
            "Authorization": f"Bearer {access_token}"
        }
        # curl -X 'GET' \
        # 'https://worldcat.org/bib/checkcontrolnumbers?oclcNumbers=123456,7890122,4455677' \
        # -H 'accept: application/atom+json' \
        # -H 'Authorization: Bearer tk_Axxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        param_str = self._list_to_param_str_(oclc_numbers)
        url = f"https://worldcat.org/bib/checkcontrolnumbers?oclcNumbers={param_str}"
        response = requests.get(url=url, headers=headers)
        # self.logger.logit(f"response: '{response.json()}'")
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
        return response.json()


    # Used to create a bibliographic record.
    # param: record in XML. 
    # return: XML record, or XML error message. 
    # <?xml version="1.0" encoding="UTF-8" standalone="yes"?> <error xmlns="http://worldcat.org/xmlschemas/response">
    #     <code type="application">WS-403</code>
    #     <message>The institution identifier provided does not match the WSKey credentials.</message>
    # </error>
    def create_bib_record(self, record_xml:str) -> str:
        access_token = self._get_access_token_()
        headers = {
            'accept': 'application/atom+xml;content="application/vnd.oclc.marc21+xml"',
            "Authorization": f"Bearer {access_token}",
            'Content-Type': 'application/vnd.oclc.marc21+xml'
        }
        url = f"https://worldcat.org/bib/data?inst={self.inst_id}&instSymbol={self.inst_symbol}"
        response = requests.post(url=url, data=record_xml, headers=headers)
        # curl -X 'POST' \
        # 'https://worldcat.org/bib/data?inst=128807&instSymbol=OCPSB' \
        # -H 'accept: application/atom+xml;content="application/vnd.oclc.marc21+xml"' \
        # -H 'Authorization: Bearer tk_tP3Q1weM8zxxxxxxxxxxxxxxxxxxxxxxMFU21ng1t' \
        # -H 'Content-Type: application/vnd.oclc.marc21+xml' \
        # -d '<?xml version="1.0" encoding="UTF-8"?> <record xmlns="http://www.loc.gov/MARC21/slim">
        #     <leader>00000nam a2200000 a 4500</leader>
        #     <controlfield tag="008">120827s2012    nyua          000 0 eng d</controlfield>
        #     <datafield tag="010" ind1=" " ind2=" ">
        #         <subfield code="a">   63011276 </subfield>
        #     </datafield>
        #     <datafield tag="040" ind1=" " ind2=" ">
        #         <subfield code="a">OCWMS</subfield>
        #         <subfield code="b">eng</subfield>
        #         <subfield code="c">OCPSB</subfield>
        #     </datafield>
        #     <datafield tag="100" ind1="0" ind2=" ">
        #         <subfield code="a">OCLC Developer Network</subfield>
        #     </datafield>
        #     <datafield tag="245" ind1="1" ind2="0">
        #         <subfield code="a">Test Record</subfield>
        #     </datafield>
        #     <datafield tag="500" ind1=" " ind2=" ">
        #         <subfield code="a">FOR OCLC DEVELOPER NETWORK DOCUMENTATION</subfield>
        #     </datafield>
        # </record>        
        # '
        return response.content()

    # Used to create a bibliographic with holdings at a specific branch.
    # param: record in XML. 
    # return: XML record, or XML error message. 
    # <?xml version="1.0" encoding="UTF-8" standalone="yes"?> <error xmlns="http://worldcat.org/xmlschemas/response">
    #     <code type="application">WS-403</code>
    #     <message>The institution identifier provided does not match the WSKey credentials.</message>
    # </error>
    def create_local_bib_record(self, record_xml:str) -> str:
        access_token = self._get_access_token_()
        headers = {
            'accept': 'application/atom+xml;content="application/vnd.oclc.marc21+xml"',
            "Authorization": f"Bearer {access_token}",
            'Content-Type': 'application/vnd.oclc.marc21+xml'
        }
        url = f"https://worldcat.org/lbd/data?inst={self.inst_id}&instSymbol={self.inst_symbol}&holdingLibraryCode=MAIN"
        response = requests.post(url=url, data=record_xml, headers=headers)
        # curl -X 'POST' \
        # 'https://worldcat.org/lbd/data?inst=128807&instSymbol=OCPSB&holdingLibraryCode=MAIN' \
        # -H 'accept: application/atom+xml;content="application/vnd.oclc.marc21+xml"' \
        # -H 'Authorization: Bearer tk_tP3Q1weM8zPY7RJkpYSCV4Y91smMFU21ng1t' \
        # -H 'Content-Type: application/vnd.oclc.marc21+xml' \
        # -d '<?xml version="1.0" encoding="UTF-8"?> <record xmlns="http://www.loc.gov/MARC21/slim">
        #     <leader>00000n   a2200000   4500</leader>
        #     <controlfield tag="004">99999999999999999999999</controlfield>
        #     <datafield tag="240" ind1="1" ind2="4">
        #         <subfield code="a">UniformTitleF</subfield>
        #         <subfield code="l">LanguageOfWork</subfield>
        #         <subfield code="g">OCL</subfield>
        #     </datafield>
        #     <datafield tag="500" ind1=" " ind2=" ">
        #         <subfield code="a">FOR OCLC DEVELOPER NETWORK DOCUMENTATION</subfield>
        #     </datafield>
        #     <datafield tag="935" ind1=" " ind2=" ">
        #         <subfield code="a">MyLocalSystemNumber</subfield>
        #     </datafield>
        #     <datafield tag="940" ind1=" " ind2=" ">
        #         <subfield code="a">OCWMS</subfield>
        #     </datafield>
        # </record>                                               
        # '
        return response.content()

    # Used to update a bibliographic with holdings at a specific branch.
    # param: record in XML. 
    # return: XML record, or XML error message. HTTP code 200.
    # <?xml version="1.0" encoding="UTF-8" standalone="yes"?> <error xmlns="http://worldcat.org/xmlschemas/response">
    #     <code type="application">WS-403</code>
    #     <message>The institution identifier provided does not match the WSKey credentials.</message>
    # </error>
    def update_bib_record(self, record_xml:str) -> str:
        access_token = self._get_access_token_()
        headers = {
            'accept': 'application/atom+xml;content="application/vnd.oclc.marc21+xml"',
            "Authorization": f"Bearer {access_token}",
            'Content-Type': 'application/vnd.oclc.marc21+xml'
        }
        url = f"https://worldcat.org/bib/data?inst={self.inst_id}&instSymbol={self.inst_symbol}"
        response = requests.put(url=url, data=record_xml, headers=headers)
        # curl -X 'PUT' \
        # 'https://worldcat.org/bib/data?inst=128807&instSymbol=OCPSB' \
        # -H 'accept: application/atom+xml;content="application/vnd.oclc.marc21+xml"' \
        # -H 'Authorization: Bearer tk_tP3Q1weM8zPY7RJkpYSCV4Y91smMFU21ng1t' \
        # -H 'Content-Type: application/vnd.oclc.marc21+xml' \
        # -d '<?xml version="1.0" encoding="UTF-8"?> <record xmlns="http://www.loc.gov/MARC21/slim">
        #     <leader>00000nam a2200000 a 4500</leader>
        #     <controlfield tag="001">99999999999999999999999</controlfield>
        #     <controlfield tag="008">120827s2012    nyua          000 0 eng d</controlfield>
        #     <datafield tag="010" ind1=" " ind2=" ">
        #         <subfield code="a">   63011276 </subfield>
        #     </datafield>
        #     <datafield tag="040" ind1=" " ind2=" ">
        #         <subfield code="a">OCWMS</subfield>
        #         <subfield code="c">OCWMS</subfield>
        #     </datafield>
        #     <datafield tag="100" ind1=" " ind2="0">
        #         <subfield code="a">OCLC Developer Network</subfield>
        #     </datafield>
        #     <datafield tag="245" ind1="4" ind2="0">
        #         <subfield code="a">Test Record</subfield>
        #     </datafield>
        #     <datafield tag="500" ind1=" " ind2=" ">
        #         <subfield code="a">FOR OCLC DEVELOPER NETWORK DOCUMENTATION</subfield>
        #     </datafield>
        # </record>      
        # '
        # Response XML like:
        # <?xml version="1.0" encoding="UTF-8"?> <entry xmlns="http://www.w3.org/2005/Atom">
        # <content type="application/xml">
        #     <response xmlns="http://worldcat.org/rb" mimeType="application/vnd.oclc.marc21+xml">
        #         <record xmlns="http://www.loc.gov/MARC21/slim">
        #             <leader>00000cam a2200000 a 4500</leader>
        #             <controlfield tag="001">ocn311684437</controlfield>
        #             <controlfield tag="003">OCoLC</controlfield>
        #             <controlfield tag="005">20200327224019.6</controlfield>
        #             <controlfield tag="008">080916s2009    paua          000 1 eng  </controlfield>
        #             <datafield tag="010" ind1=" " ind2=" ">
        #                 <subfield code="a">  2008937609</subfield>
        #             </datafield>
        #             <datafield tag="040" ind1=" " ind2=" ">
        #                 <subfield code="a">DLC</subfield>
        #   ... 
        # and a HTTP code of 200
        return response.content()

    # Create / set institutional holdings. Used to let OCLC know a library has a title. 
    # param: List of oclc numbers as strings. The max number of numbers will be batch posted
    #   and the remaining returned.
    # return: json dict response object.
    # The successful request is returned:
    # {
    # "entries": [
    #     {
    #     "title": "44321120",
    #     "content": {
    #         "requestedOclcNumber": "44321120",
    #         "currentOclcNumber": "37264396",
    #         "institution": "OCWMS",
    #         "status": "HTTP 403 Forbidden",
    #         "detail": "Unauthorized 040 $c symbol for pilot modification.",
    #         "id": "http://worldcat.org/oclc/37264396"
    #     },
    #     "updated": "2015-04-02T14:52:00.852Z"
    #     },
    #     {
    #     "title": "896872613",
    #     "content": {
    #         "requestedOclcNumber": "896872613",
    #         "currentOclcNumber": "896872613",
    #         "institution": "OCWMS",
    #         "status": "HTTP 200 OK",
    #         "id": "http://worldcat.org/oclc/896872613"
    #     },
    #     "updated": "2015-04-02T14:52:00.880Z"
    #     },
    #     {
    #     "title": "99999999999",
    #     "content": {
    #         "requestedOclcNumber": "99999999999",
    #         "currentOclcNumber": "99999999999",
    #         "institution": "OCWMS",
    #         "status": "HTTP 404 Not Found",
    #         "detail": "Record not found for holdings operation",
    #         "id": "http://worldcat.org/oclc/99999999999"
    #     },
    #     "updated": "2015-04-02T14:52:00.881Z"
    #     }
    # ],
    # "extensions": [
    #     {
    #     "name": "os:totalResults",
    #     "attributes": {
    #         "xmlns:os": "http://a9.com/-/spec/opensearch/1.1/"
    #     },
    #     "children": [
    #         "3"
    #     ]
    #     },
    #     ...
    # ]
    # }
    def set_holdings(self, oclc_numbers:list) -> dict:
        access_token = self._get_access_token_()
        headers = {
            "accept": "application/atom+json",
            "Authorization": f"Bearer {access_token}"
        }
        param_str = self._list_to_param_str_(oclc_numbers)
        url = f"https://worldcat.org/ih/datalist?oclcNumbers={param_str}&inst={self.inst_id}&instSymbol={self.inst_symbol}"
        # print(f"DEBUG:===> url is {url} is that what you expected?")
        response = requests.post(url=url, headers=headers)
        # curl -X 'POST' \
        # 'https://worldcat.org/ih/datalist?oclcNumbers=777890&inst=128807&instSymbol=OCPSB' \
        # -H 'accept: application/atom+json' \
        # -H 'Authorization: Bearer xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' \
        # -d ''
        # https://worldcat.org/ih/datalist?oclcNumbers=777890&inst=128807&instSymbol=OCPSB
        # The response is usually empty, with an HTTP code of 201
        return response.status_code, response.json()

    # Unset / delete institutional holdings. Used to let OCLC know we don't have a title anymore.
    # param: oclcNumbers - list of oclc integers, as strings. The method will send the max allowable,
    #  (50), or the max contents of the argument list, which ever is smaller.
    # param: cascade - int 
    #  Whether or not to execute the operation if a local holdings record, or local biblliographic record
    #  exists. 0 - don't remove holdings if local holding record or local bibliographic record exists 
    #  1 - yes remove holdings and delete local holdings record or local bibliographic record exists.
    # return: json response object. 
    # The response from the web service is an empty dictionary.
    def unset_holdings(self, oclc_numbers:list, cascade:int = 1) -> dict:
        access_token = self._get_access_token_()
        headers = {
            "accept": "application/atom+json",
            "Authorization": f"Bearer {access_token}"
        }
        param_str = self._list_to_param_str_(oclc_numbers)
        url = f"https://worldcat.org/ih/datalist?oclcNumbers={param_str}&cascade={cascade}&inst={self.inst_id}&instSymbol={self.inst_symbol}"
        response = requests.delete(url=url, headers=headers)
        # curl -X 'DELETE' \
        # 'https://worldcat.org/ih/datalist?oclcNumbers=1234567,2332344&cascade=1&inst=128807&instSymbol=OCPSB' \
        # -H 'accept: application/atom+json' \
        # -H 'Authorization: Bearer xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        # Request URL
        # https://worldcat.org/ih/datalist?oclcNumbers=1234567,2332344&cascade=1&inst=128807&instSymbol=OCPSB
        # The response can be saved to the report database.
        return response.json()

if __name__ == "__main__":
    import doctest
    doctest.testfile("oclcws.tst")