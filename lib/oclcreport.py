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
import sys

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# This class outputs a report of transactions with OCLC's web service.
# Spec for Reporting
# * Report how long the script ran.
# * Report total hits and breakdown by operation.
# * Checks should report the original sent and value returned by OCLC and if an update is required. 
# Updating this information could be in a report that could be made available to CMA for record 
# updating, but automating is out of scope for now.
# * Adds and delete counts shall be reported along with any errors.
class OclcReport:

    def __init__(self, debug:bool=False):
        self.debug = debug
        self.checks   = {'total': 0, 'success': 0, 'warnings':0, 'errors': 0}
        self.holdings = {'total': 0, 'success': 0, 'warnings':0, 'errors': 0}
        self.adds     = {'total': 0, 'success': 0, 'warnings':0, 'errors': 0}
        self.dels     = {'total': 0, 'success': 0, 'warnings':0, 'errors': 0}
        self.bibs     = {'total': 0, 'success': 0, 'warnings':0, 'errors': 0}
        # Keep track of the updated OCLC numbers. In this case use a dictionary
        # with format {old: new, ...}
        self.updates_dict = {}

    # Wrapper for the logger. Added after the class was written
    # and to avoid changing tests. 
    # param: message:str message to either log or print. 
    # param: to_stderr:bool if True and logger  
    def print_or_log(self, message, to_stderr:bool=False):
        if isinstance(message, list):
            if to_stderr:
                for m in message:
                    sys.stderr.write(f"{m}\n")
            else:
                for m in message:
                    print(f"{m}")
        else:
            if to_stderr:
                sys.stderr.write(f"{message}\n")
            else:
                print(f"{message}")


    # {'title': '46629055', 
    #  'content': 
    #       {'requestedOclcNumber': '46629055', 
    #        'currentOclcNumber': '46629055', 
    #        'institution': 'CNEDM', 
    #        'holdingCurrentlySet': False, 
    #        'id': 'http://worldcat.org/oclc/46629055'}, 
    #  'updated': '2023-04-20T22:38:06.540Z'}
    # Interprets the JSON response from the 
    # worldcat.org/ih/checkholdings?oclcNumber request. 
    # param: json response object.
    # param: debug bool value true if you want more messaging and false for less.
    # returns: True if successful and False otherwise.
    def check_holdings_response(self, 
      code:int,
      json_data:dict, 
      debug:bool=False):
        results = []
        if code < 200 or code > 207:
            msg = ''
            try:
                reported_error = f"OCLC said: {json_data}"
            except KeyError as ex:
                reported_error = f"JSON: {json_data}"
                msg = f"check response failed on {ex} attribute.\n{reported_error}\n"
            except ValueError:
                reported_error = f"JSON: was empty!"
                msg = f"check failed!"
            self.print_or_log(msg, 'error')
            self.holdings['errors'] += 1
            return False
        b_result= True
        if json_data:
            if debug:
                print(f"DEBUG: check got JSON ===>{json_data}")
            try:
                title          = json_data['title']
                updated        = json_data['updated']
                updated = updated.replace("T", " ")
                updated = updated[:-5]
                content        = json_data['content']
                old_num        = content['requestedOclcNumber']
                new_num        = content['currentOclcNumber']
                is_holding_set = content['holdingCurrentlySet']
                check_url      = content['id']
                institution    = content['institution']
                return_str     = f"?{title} is {institution} holding: {is_holding_set} as of '{updated}'"
                self.holdings['success'] += 1
                if is_holding_set:
                    if old_num == new_num:
                        return_str += f"  OCLC number confirmed"
                    else:
                        self.updates_dict[str(old_num)] = str(new_num)
                        return_str += f"  OCLC number updated to {new_num}"
                        self.holdings['warnings'] += 1
                return_str += f" See {check_url} for more information."
                results.append(return_str)
                self.holdings['total'] += 1
            except KeyError as ex:
                try:
                    reported_error = f"OCLC said: {json_data}"
                except KeyError as fx:
                    reported_error = f"JSON: {json_data}"
                msg = f"check response failed on {ex} attribute.\n{reported_error}\n"
                self.print_or_log(msg, 'error')
                results.append(msg)
                # There was a problem with the web service so stop processing.
                b_result = False
        # self.print_or_log(results)
        return b_result, results

    # Parses the response from the OCLC set holdings request.
    def set_response(self, 
      code:int, 
      json_data:dict,
      debug:bool=False):
        results = []
        if code < 200 or code > 207:
            msg = ''
            try:
                reported_error = f"OCLC said: {json_data}"
            except KeyError as ex:
                reported_error = f"JSON: {json_data}"
                msg = f"set response failed on {ex} attribute.\n{reported_error}\n"
            except ValueError:
                reported_error = f"JSON: was empty!"
                msg = f"set failed!"
            self.print_or_log(msg, 'error')
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
                        return_str += f"  added. See http://worldcat.org/oclc/{old_num}"
                        self.adds['success'] += 1
                    else:
                        return_str += f"  updated to {new_num}. See http://worldcat.org/oclc/{new_num}"
                        self.updates_dict[str(old_num)] = str(new_num)
                        detail = entry['content']['detail']
                        if detail:
                            return_str += f", {detail}"
                            self.adds['warnings'] += 1
                    results.append(return_str)
                    self.adds['total'] += 1
            except KeyError as ex:
                try:
                    reported_error = f"OCLC said: {json_data}"
                except KeyError as ex:
                    reported_error = f"JSON: {json_data}"
                msg = f"set response failed on {ex} attribute.\n{reported_error}\n"
                self.print_or_log(msg, 'error')
                self.adds['errors'] += 1
                results.append(msg)
                b_result = False
        # self.print_or_log(results)
        return b_result, results

    # Checks the results of the delete transaction.
    def delete_response(self, 
      code:int, 
      json_data:dict,
      debug:bool=False):
        results = []
        # Check the HTTP code. Should be 207 but will accept 200 to 207
        if code < 200 or code > 207:
            msg = ''
            try:
                reported_error = f"OCLC said: {json_data}"
            except KeyError as ex:
                reported_error = f"JSON: {json_data}"
                msg = f"delete response failed on {ex} attribute.\n{reported_error}\n"
            except ValueError:
                reported_error = f"JSON: was empty!"
                msg = f"delete failed!"
            self.print_or_log(msg, 'error')
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
                        return_str += f"  deleted"
                        self.dels['success'] += 1
                    else:
                        return_str += f"  updated to {new_num}"
                        detail = entry['content']['detail']
                        if detail:
                            return_str += f", {detail}"
                            self.dels['warnings'] += 1
                    results.append(return_str)
                    self.dels['total'] += 1
            except KeyError as ex:
                try:
                    reported_error = f"OCLC said: {json_data}"
                except KeyError as ex:
                    reported_error = f"JSON: {json_data}"
                msg = f"delete response failed on {ex} attribute.\n{reported_error}\n"
                self.print_or_log(msg, 'error')
                self.dels['errors'] += 1
                results.append(msg)
                b_result = False
        # self.print_or_log(results)
        return b_result, results

    # Parses an expected (XML) web service result.  
    def create_bib_response(self, response, debug:bool=False):
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

    # Returns the check holdings tally. 
    # return: dictionary of holdings results.
    def get_check_holdings_results(self) ->dict:
        return self.holdings

    # Gets the dictionary of updated OCLC numbers 
    # where the key is the old number and the value
    # is the new number.
    def get_updated(self) ->dict:
        return self.updates_dict

if __name__ == "__main__":
    import doctest
    doctest.testfile("oclcreport.tst")