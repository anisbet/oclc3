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
import sys
import re
from os.path import exists

IS_TEST = False

# This class will take a flat file and stream or collect all the DOCUMENT, FORM
# sentenials, the 001, and all 035 tags. When an OCLC tag is encountered it will
# be assumed to be a set record. 
# 
# If the number was set successfully the record will be discarded. If the 
# response contains an updated the record will be modified, and concatinated 
# to slim file in preparation for 'catalogmerge'. 
class Flat:
    def __init__(self, flat_file:str, configs:dict={}):
        self.flat = flat_file
        self.debug= configs.get("debug")
        if self.debug:
            print(f"DEBUG: reading {self.flat}")
        if not exists(self.flat):
            sys.stderr.write(f"*error, no such flat file: '{self.flat}'.\n")
        # Read FLAT file record by record.
        # Store the slim bib record as follows 
        # {'1234567':{
        #   'reject': False,
        #   'form': 'FORM=MUSIC', 
        #   'tcn': 'on123456', 
        #   'oclc': '1234567', 
        #   '035': ["(SIRSI) 035_0", "(OCM) 035_1", ...]},
        # ...}
        self.slim_bib_records = self._read_bib_records_(self.flat)
        if IS_TEST:
            print(f"{self.slim_bib_records}")

    # Tests the necessary conditions of a well-formed slim record.
    # Those conditions are; it must have a '001', an OCLC number,
    # it must not be empty, and it must have a form identifier.
    # param: record:dict if empty a 'reject' value of True is added,
    #   and any other missing pieces update the 'reject' field of 
    #   the record. 
    # return: True if the record is well formed and False otherwise.   
    def _is_wellformed_(self, record:dict):
        if not record:
            return False
        elif not record.get('form'):
            return False
        elif not record.get('001'):
            return False
        else:
            return True

    # Reads a single bib record
    def _read_bib_records_(self, flat):
        document_sentinal = re.compile(r'^\*\*\* DOCUMENT BOUNDARY \*\*\*[\s+]?$')
        form_sentinal     = re.compile(r'^FORM=')
        tcn               = re.compile(r'^\.001\.\s+')
        zero_three_five   = re.compile(r'^\.035\.\s+')
        oclc_num_matcher  = re.compile(r'\(OCoLC\)')
        record  = {}
        records = {}
        with open(flat, encoding='ISO-8859-1', mode='r') as f:
            line_num = 0
            # If there is no OCLC number in the record don't store the bib and issue a warning
            # If there is more than one, replace the previous one. In the end which ever remains
            # will be checked and possibly replaced, but all the extras will be removed; so a 
            # form of clean up will be done.
            oclc_num_count = 0
            # This is the number of records read from the flat file.
            records_read = 0
            oclc_number = ''
            for l in f:
                line_num += 1
                line = l.rstrip()
                # We are interested in the following tags from the flat input
                # *** DOCUMENT BOUNDARY ***
                if re.search(document_sentinal, line):
                    records_read += 1
                    if self.debug:
                        print(f"DEBUG: found document boundary on line {line_num}")
                    # close previous record if open, and open new record
                    if self._is_wellformed_(record):
                        if oclc_num_count > 1:
                            print(f"*warning, TCN {record['001']} contains multiple OCLC numbers. Only the last will be checked and updated as necessary.")
                        if oclc_number:
                            records[str(oclc_number)] = record
                        else:
                            print(f"*warning, rejecting TCN {record['001']} as malformed; possibly missing OCLC number.")
                    record = {}
                    record['001'] = ''
                    record['form'] = ''
                    record['035'] = []
                    oclc_number = ''
                    oclc_num_count = 0
                    continue
                # FORM=MUSIC 
                if re.search(form_sentinal, line):
                    # Just add it 
                    if self.debug:
                        print(f"DEBUG: found form description on line {line_num}")
                    record['form'] = line
                    continue
                # .001. |aon1347755731  
                if re.search(tcn, line):
                    record['001'] = line.split("|a")[1]
                    if self.debug:
                        print(f"DEBUG: found TCN {record['001']} on line {line_num}")
                    continue
                # TODO: Add configurable tag and value rejection functionality. Like '250': 'On Order' = 'reject': True.
                # .035.   |a(OCoLC)987654321
                # .035.   |a(Sirsi) 111111111
                if re.search(zero_three_five, line):
                    # If this has an OCoLC then save as a 'set' number otherwise just record it as a regular 035.
                    if re.search(oclc_num_matcher, line):
                        oclc_num_count += 1
                        oclc_number = line.split("|a(OCoLC)")[1]
                        if self.debug:
                            print(f"DEBUG: found an OCLC number ({oclc_number}) on line {line_num}")
                    else:
                        record['035'].append(line.split("|a")[1])
                        if self.debug:
                            print(f"DEBUG: found an 035 on line {line_num} ({line})")
                    continue
        # End of the document; there are no more document boundaries to signal a new record.
        if not self._is_wellformed_(record):
            print(f"*warning, TCN {record['001']} rejected.")
            print(f"{len(records)} OCLC updates possible from {records_read} records read.")
            return records
        if oclc_num_count > 1:
            print(f"*warning, TCN {record['001']} contains multiple OCLC numbers. Only the last will be checked and updated as necessary.")
        records[str(oclc_number)] = record
        print(f"{len(records)} OCLC updates possible from {records_read} records read.")
        return records

    # This method will return a 'set' or add list.
    def get_local_list(self):
        # TODO: return list with '+#######'.
        return self.slim_bib_records.keys()

    # Pass the dictionary of new and old OCLC numbers. This method
    # will update the slim flat records and output to a file called
    # <input>.slim.flat
    def update_slim_flat(self, log:dict):
        pass

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    doctest.testfile("flat.tst")