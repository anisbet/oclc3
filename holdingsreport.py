###############################################################################
#
# Purpose: Read OCLC holdings report.
# Date:    Wed 09 Aug 2023 01:12:14 PM EDT
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

import sys
from os import linesep
import os.path as path
from log import Log

IS_TEST = True

# This class is responsible for reading and parsing the OCLC holding
# report into a list. 
class HoldingsReport:

    def __init__(self, reportFile:str, debug:bool=False, logger:Log=None):
        self.report = reportFile
        self.debug  = debug
        self.logger = logger
        self.oclc_numbers = []
        if self.debug:
            print(f"DEBUG: reading {self.report}")
        if not path.exists(self.report):
            sys.stderr.write(f"*error, no such report file: '{self.report}'." + linesep)
        # Test that the class can read this type of report
        self.report_path, ext = path.splitext(self.report)
        if ext.lower() == '.csv' or ext.lower() == '.tsv':
            self.oclc_numbers = self._read_csv_(self.report)
        else:
            sys.stderr.write(f"*error, file type: '{ext}' not supported yet." + linesep)
        if IS_TEST:
            self.print_or_log(f"{self.oclc_numbers}")

    # Wrapper for the logger. Added after the class was written
    # and to avoid changing tests. 
    # param: message:str message to either log or print. 
    # param: to_stderr:bool if True and logger  
    def print_or_log(self, message:str, to_stderr:bool=False):
        if self.logger:
            if to_stderr:
                self.logger.logit(message, level='error', include_timestamp=True)
            else:
                self.logger.logit(message)
        elif to_stderr:
            sys.stderr.write(f"{message}" + linesep)
        else:
            print(f"{message}")

    # Reads a CSV file using pandas.
    # param: CSV file report, and if None then the file supplied to the constructor. 
    #   Optional for testing.
    # return: list of oclc numbers.
    def _read_csv_(self, report:str) -> list:
        line_count = 0
        with open(report, encoding='ISO-8859-1', mode='r') as csv:
            for line in csv:
                fields = line.split('\t')
                hyperlink = fields[0]
                if hyperlink:
                    hyperlink_alt_text = hyperlink.split(', "')
                    if len(hyperlink_alt_text) > 0:
                        oclc_num = hyperlink_alt_text[1][0:-2]
                        if line_count < 5 and IS_TEST:
                            print(f"{line_count} => {oclc_num}")
                        self.oclc_numbers.append(oclc_num)
                    elif self.debug:
                        self.print_or_log(f"expected hyperlink data on line {line_count}")
                line_count += 1
        self.print_or_log(f"read {len(self.oclc_numbers)} records.")
        return self.oclc_numbers               

    def get_remote_numbers(self) ->list:
        return self.oclc_numbers
        
    # Writes the OCLC numbers to file.
    # param: fileName:str if provided the file will be so-named, however 
    #   by default the name of the original report will be used including 
    #   any path in formation. For example ../report.csv will by default
    #   become ../report.lst 
    def write_list(self, fileName:str=None):
        out_file = self.report_path + '.lst'
        if fileName:
            out_file = fileName
        with open(out_file, encoding='ISO-8859-1', mode='w') as f:
            for num in self.oclc_numbers:
                f.write(f"{num}\n")
            f.close()
        if self.debug:
            self.print_or_log(f"wrote {len(self.oclc_numbers)} records to {out_file}.")

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    doctest.testfile("holdingsreport.tst")