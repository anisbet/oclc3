###############################################################################
#
# Purpose: Reporting for WorldCat Metadata API.
# Date:    Tue Mar 21 12:47:45 PM EDT 2023
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
import json
from os.path import dirname, join, exists
from datetime import datetime
import re
from log import Log

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# This class outputs a report of transactions with OCLC's web service.
# Spec for Reporting
# * Report how long the script ran.
# * Report total hits and breakdown by operation.
# * Checks should report the original sent and value returned by OCLC and if an update is required. Updating this information could be in a report that could be made available to CMA for record updating, but automating is out of scope for now.
# * Adds and delete counts shall be reported along with any errors.
# * The master list (receipt) shall be updated with what happened with either of the following.
#   * ` - success` if everything went as planned.
#   * ` - error [reason]`, on error output the error.
#   * ` - pending` if the web service hit count exceeded quota
#   * ` - old: [old], new: [new]` if the two numbers differ, and ` - success` if no change required.
class OclcReport:

    def __init__(self, logger:Log, debug:bool=False):
        self.debug = debug
        self.checks = {'total': 0, 'success': 0, 'warnings':0, 'errors': 0}
        self.adds   = {'total': 0, 'success': 0, 'warnings':0, 'errors': 0}
        self.dels   = {'total': 0, 'success': 0, 'warnings':0, 'errors': 0}
        self.bibs   = {'total': 0, 'success': 0, 'warnings':0, 'errors': 0}
        self.logger = logger

    # Interprets the JSON response from the 
    # worldcat.org/bib/checkcontrolnumbers request. 
    # param: json response object.
    # param: debug bool value true if you want more messaging and false for less.
    # returns: list of requested OCLC numbers with the results of the check 
    # query for each.
    # 
    # For example: ['?12345 - success', '?67890 - updated to 6777790', 
    # '?999999999 - error Record not found.']
    def check_response(self, json_data:dict, debug:bool=False) ->bool:
        results = []
        b_result= True
        if json_data:
            if debug:
                print(f"DEBUG: check got JSON ===>{json_data}")
            try:
                entries = json_data['entries']
                for entry in entries:
                    title   = entry['title']
                    old_num = entry['content']['requestedOclcNumber']
                    new_num = entry['content']['currentOclcNumber']
                    # code    = int(re.search(r'\b\d{3}\b', entry['content']['status']).group())
                    found   = entry['content']['found']
                    return_str = f"?{title}"
                    if found:
                        if old_num == new_num:
                            return_str += f" - success"
                            self.checks['success'] += 1
                        else:
                            return_str += f" - updated to {new_num}"
                            self.checks['warnings'] += 1
                    else:
                        detail = entry['content']['detail']
                        return_str += f" - error not found message: {detail}"
                        self.checks['errors'] += 1
                    results.append(return_str)
                    self.checks['total'] += 1
            except KeyError as ex:
                try:
                    reported_error = f"OCLC said: {json_data['message']}"
                except KeyError as fx:
                    reported_error = f"JSON: {json_data}"
                msg = f"check response failed on {ex} attribute.\n{reported_error}\n"
                self.logger.logit(msg, 'error')
                results.append(msg)
                # There was a problem with the web service so stop processing.
                b_result = False
        self.logger.logem(results)
        return b_result

    # The oclc_nums_sent looks like: '850939592,850939596'
    # Success
    # -------
    # {
    #   "entries": [
    #     {
    #       "title": "44321120",
    #       "content": {
    #         "requestedOclcNumber": "44321120",
    #         "currentOclcNumber": "37264396",
    #         "institution": "OCWMS",
    #         "status": "HTTP 403 Forbidden",
    #         "detail": "Unauthorized 040 $c symbol for pilot modification.",
    #         "id": "http://worldcat.org/oclc/37264396"
    #       },
    #       "updated": "2015-04-02T14:52:00.852Z"
    #     },
    #  ...
    def set_response(self, 
      code:int, 
      json_data:dict,
      debug:bool=False) ->bool:
        results = []
        if code < 200 or code > 207:
            msg = ''
            try:
                reported_error = f"OCLC said: {json_data['message']}"
            except KeyError as ex:
                reported_error = f"JSON: {json_data}"
                msg = f"set response failed on {ex} attribute.\n{reported_error}\n"
            except TypeError:
                reported_error = f"JSON: was empty!"
                msg = f"set failed!"
            self.logger.logit(msg, 'error')
            self.adds['errors'] += 1
            return False
        b_result= True
        if json_data:
            if debug:
                print(f"DEBUG: set got JSON ===>{json_data}")
            try:
                entries = json_data['entries']
                for entry in entries:
                    title   = entry['title']
                    old_num = entry['content']['requestedOclcNumber']
                    new_num = entry['content']['currentOclcNumber']
                    return_str = f"+{title}"
                    if old_num == new_num:
                        return_str += f" - success"
                        self.adds['success'] += 1
                    else:
                        return_str += f" - updated to {new_num}"
                        detail = entry['content']['detail']
                        if detail:
                            return_str += f", {detail}"
                            self.adds['warnings'] += 1
                    results.append(return_str)
                    self.adds['total'] += 1
            except KeyError as ex:
                try:
                    reported_error = f"OCLC said: {json_data['message']}"
                except KeyError as ex:
                    reported_error = f"JSON: {json_data}"
                msg = f"set response failed on {ex} attribute.\n{reported_error}\n"
                self.logger.logit(msg, 'error')
                self.adds['errors'] += 1
                results.append(msg)
                b_result = False
        self.logger.logem(results)
        return b_result

    # Checks the results of the delete transaction.
    def delete_response(self, 
      code:int, 
      json_data:dict,
      debug:bool=False) ->bool:
        results = []
        # Check the HTTP code. Should be 207 but will accept 200 to 207
        if code < 200 or code > 207:
            msg = ''
            try:
                reported_error = f"OCLC said: {json_data['message']}"
            except KeyError as ex:
                reported_error = f"JSON: {json_data}"
                msg = f"delete response failed on {ex} attribute.\n{reported_error}\n"
            except TypeError:
                reported_error = f"JSON: was empty!"
                msg = f"delete failed!"
            self.logger.logit(msg, 'error')
            self.dels['errors'] += 1
            return False
        # Otherwise carry on parsing results.
        results = []
        b_result= True
        if json_data:
            if debug:
                print(f"DEBUG: delete got JSON ===>{json_data}")
            try:
                entries = json_data['entries']
                for entry in entries:
                    title   = entry['title']
                    old_num = entry['content']['requestedOclcNumber']
                    new_num = entry['content']['currentOclcNumber']
                    return_str = f"-{title}"
                    if old_num == new_num:
                        return_str += f" - success"
                        self.adds['success'] += 1
                    else:
                        return_str += f" - updated to {new_num}"
                        detail = entry['content']['detail']
                        if detail:
                            return_str += f", {detail}"
                            self.adds['warnings'] += 1
                    results.append(return_str)
                    self.adds['total'] += 1
            except KeyError as ex:
                try:
                    reported_error = f"OCLC said: {json_data['message']}"
                except KeyError as ex:
                    reported_error = f"JSON: {json_data}"
                msg = f"delete response failed on {ex} attribute.\n{reported_error}\n"
                self.logger.logit(msg, 'error')
                self.adds['errors'] += 1
                results.append(msg)
                b_result = False
        self.logger.logem(results)
        return b_result


    def create_bib_response(self, response:str, debug:bool=False):
        # Should see this in the response.
        # <controlfield tag="004">99999999999999999999999</controlfield>
        # TODO: use beautiful soup to convert the response. 
        if not response:
            self.bibs['errors'] += 1
            return False
        if debug:
            print(f"DEBUG: bib upload: '{response}'")
        if '<controlfield ' in response:
            self.bibs['success'] += 1
            return True
        self.bibs['errors'] += 1
        return False

    # Returns the checks result tally dictionary. 
    # return: dictionary of check tally results.
    def get_check_results(self) ->dict:
        return self.checks

    # Returns the set result tally dictionary. 
    # return: dictionary of set tally results.
    def get_set_holdings_results(self) ->dict:
        return self.adds

    # Returns the unset or delete result tally. 
    # return: dictionary of set tally results.
    def get_delete_holdings_results(self) ->dict:
        return self.dels

    # Returns the bib record load tally. 
    # return: dictionary of bib load results.
    def get_bib_load_results(self) ->dict:
        return self.bibs

if __name__ == "__main__":
    import doctest
    doctest.testfile("oclcreport.tst")