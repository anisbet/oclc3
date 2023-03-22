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
import yaml
from datetime import datetime
import re

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

    def __init__(self, yaml_path:str='test.yaml', debug:bool=False):
        # Since this file is in the lib/ below the caller.
        yaml_file = join(dirname(__file__), '..', yaml_path)
        if exists(yaml_file):
            with open(yaml_file) as f:
                try:
                    self.configs = yaml.safe_load(f)
                    self.report_file = self.configs['report']
                except yaml.YAMLError as exc:
                    sys.stderr.write(f"{exc}")
            f.close()
            if debug:
                print(f"yaml loaded.")
        else:
            sys.stderr.write(f"*error, yaml file not found! Expected '{yaml_file}'")
            sys.exit()
        self.debug = debug
        self.checks = {'total': 0, 'success': 0, 'errors': 0}
        self.adds = {'total': 0, 'success': 0, 'errors': 0}
        self.dels = {'total': 0, 'success': 0, 'errors': 0}

    # Logs entries with timestamps.
    # param: message str to write to log. 
    # param: level string values can be 'error', 'info'. Default 'info'.
    # return: the time-stamped, formatted error message as was written to the log.
    def logit(self, message:str, level:str='info') -> str:
        time_str = datetime.now().strftime(DATE_FORMAT)
        if level == 'error':
            msg = f"[{time_str}] *error, {message}"
        else:
            msg = f"[{time_str}] {message}"
        with open(self.report_file, encoding='utf-8', mode='a') as log:
            log.write(f"{msg}")
        log.close()
        return msg

    # Interprets the JSON response from the 
    # worldcat.org/bib/checkcontrolnumbers request. 
    # param: json response object.
    # param: debug bool value true if you want more messaging and false for less.
    # returns: list of requested OCLC numbers with the results of the check 
    # query for each.
    # 
    # For example: ['?12345 - success', '?67890 - updated to 6777790', 
    # '?999999999 - error Record not found.']
    def check_response(self, json_data:dict, debug:bool=False) -> list:
        results = []
        if json_data:
            entries = json_data['entries']
            try:
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
                        else:
                            return_str += f" - updated to {new_num}"
                        self.checks['success'] += 1
                    else:
                        detail = entry['content']['detail']
                        return_str += f" - error {detail}"
                        self.checks['errors'] += 1
                    results.append(return_str)
                    self.checks['total'] += 1
            except KeyError as ex:
                msg = f"check response failed while parsing {ex} attribute"
                results.append(self.logit(msg, 'error'))
        return results

    def add_response(self, code:int, json_data:dict, debug:bool=False):
        pass

    def delete_response(self, code:int, json_data:dict, debug:bool=False):
        pass

    def __str__(self):
        pass

if __name__ == "__main__":
    import doctest
    doctest.testfile("../tests/oclcreport.tst")