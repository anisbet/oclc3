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
from os import linesep
from log import Log

IS_TEST = False

# This class will take a flat file and stream or collect all the DOCUMENT, FORM
# sentenials, the 001, and all 035 tags. When an OCLC tag is encountered it will
# be assumed to be a set record. 
# 
# If the number was set successfully the record will be discarded. If the 
# response contains an updated the record will be modified, and concatinated 
# to slim file in preparation for 'catalogmerge'. 
class Flat:
    def __init__(self, flat_file:str, debug:bool=False, logger:Log=None):
        self.flat = flat_file
        self.debug= debug
        self.logger = logger
        if self.debug:
            print(f"DEBUG: reading {self.flat}")
        if not exists(self.flat):
            sys.stderr.write(f"*error, no such flat file: '{self.flat}'." + linesep)
        # Read FLAT file record by record.
        # Store the slim bib record as follows 
        # {'1234567':{
        #   'form': 'FORM=MUSIC', 
        #   '001': 'on123456', 
        #   '035': ["(SIRSI) 035_0", "(OCM) 035_1", ...]},
        # ...}
        self.slim_bib_records = self._read_bib_records_(self.flat)
        if IS_TEST:
            self.print_or_log(f"{self.slim_bib_records}")

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
                        self.print_or_log(f"DEBUG: found document boundary on line {line_num}")
                    # close previous record if open, and open new record
                    if self._is_wellformed_(record):
                        if oclc_num_count > 1:
                            self.print_or_log(f"*warning, TCN {record['001']} contains multiple OCLC numbers. Only the last will be checked and updated as necessary.")
                        if oclc_number:
                            records[str(oclc_number)] = record
                        else:
                            self.print_or_log(f"*warning, rejecting TCN {record['001']} as malformed; possibly missing OCLC number.")
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
                        self.print_or_log(f"DEBUG: found form description on line {line_num}")
                    record['form'] = line
                    continue
                # .001. |aon1347755731  
                if re.search(tcn, line):
                    record['001'] = line.split("|a")[1]
                    if self.debug:
                        self.print_or_log(f"DEBUG: found TCN {record['001']} on line {line_num}")
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
                            self.print_or_log(f"DEBUG: found an OCLC number ({oclc_number}) on line {line_num}")
                    else:
                        record['035'].append(line.split("|a")[1])
                        if self.debug:
                            self.print_or_log(f"DEBUG: found an 035 on line {line_num} ({line})")
                    continue
        # End of the document; there are no more document boundaries to signal a new record.
        if not self._is_wellformed_(record):
            self.print_or_log(f"*warning, TCN {record['001']} rejected.")
            self.print_or_log(f"{len(records)} OCLC updates possible from {records_read} records read.")
            return records
        if oclc_num_count > 1:
            self.print_or_log(f"*warning, TCN {record['001']} contains multiple OCLC numbers. Only the last will be checked and updated as necessary.")
        records[str(oclc_number)] = record
        self.print_or_log(f"{len(records)} OCLC updates possible from {records_read} records read.")
        return records

    # This method will return a 'set' or add list.
    def get_local_list(self):
        return list(self.slim_bib_records.keys())

    # Pass the dictionary of new and old OCLC numbers. This method
    # will update the slim flat records and output to a file called
    # <input>.slim.flat.
    # Search for the old reference in the list of OCLC numbers the library
    # holds, if found remove it from the flat dictionary and replace the record
    # with the new key. Make sure to report if the updated OCLC number key
    # exists already. It is not an error if the old key can't be found. It just
    # means that the log file wasn't truncated to just the previous run, and 
    # may contain records to update from previous times. 
    # param: oclc_updates: dict of the old numbers as keys and new
    #   updated numbers as values. 
    # return: result:bool True if the slim file was successfully written
    #   with some updates, and False if the file wasn't written, there
    #   were no updates to write, or none of the requested updates could
    #   be found in the original input flat file. 
    def update_and_write_slim_flat(self, oclc_updates:dict) -> bool:
        if not oclc_updates:
            self.print_or_log(f"No OCLC updates detected.")
            return False
        # Make up a new file name for the updated slim file.
        slim_file = f"{self.flat}.updated"
        total_flat_records_submitted = len(self.slim_bib_records)
        # This is the number of records read from the flat file.
        update_count = 0
        with open(slim_file, encoding='ISO-8859-1', mode='w') as s:
            for (old_num, new_num) in oclc_updates.items():
                # Don't update is there was any hint that a problem happened.
                if not old_num or not new_num:
                    continue
                try:
                    # self.print_or_log(f"self.slim_bib_records={self.slim_bib_records}")
                    record = self.slim_bib_records.pop(old_num)
                    # self.print_or_log(f"old_num={old_num} : record={record}")
                    # Write out the slim flat data.
                    s.write(f"*** DOCUMENT BOUNDARY ***" + linesep)
                    s.write(f"{record['form']}" + linesep)
                    s.write(f".001. |a{record['001']}" + linesep)
                    s.write(f".035.   |a(OCoLC){new_num}" + linesep)
                    for zero35 in record['035']:
                        s.write(f".035.   |a{zero35}" + linesep)
                    update_count += 1
                except KeyError:
                    # This can happen if an old log file is old or contains several submissions.
                    self.print_or_log(f"Ignoring '{old_num}' because it is not included in the submitted flat file.")
        if update_count <= 0:
            self.print_or_log(f"No bibs records needed updating.")
            return False
        else:
            self.print_or_log(f"Total flat records submitted: {total_flat_records_submitted}")
            self.print_or_log(f"OCLC request-to-update responses: {len(oclc_updates)}")
            self.print_or_log(f"Total bib updates written to {slim_file}: {update_count}")
        return True

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    doctest.testfile("flat.tst")