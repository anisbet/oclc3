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

###############################################################################
#
# NOTE: Not used, but could be part of future development.
#
###############################################################################

import sqlite3
import yaml
from os.path import dirname, join, exists

#########
# Typical response:
# Typical JSON response for two records.
# {"entries": [
#     {"title": "850939592", 
#         "content": {
#             "requestedOclcNumber": "850939592", 
#             "currentOclcNumber": "850939592", 
#             "institution": "OCPSB", "status": "HTTP 200 OK", "detail": "Record found.", 
#             "id": "http://worldcat.org/oclc/850939592", 
#             "found": true, 
#             "merged": False
#         }, 
#         "updated": "2023-01-31T20:39:40.088Z"
#     }]
# }

#########
# Database Schema:
# CREATE TABLE added (
#     title TEXT,
#     requestedOclcNumber TEXT,
#     currentOclcNumber TEXT,
#     institution TEXT,
#     status TEXT,
#     detail TEXT,
#     id TEXT,
#     found TEXT,
#     merged TEXT,
#     updated TEXT
# );

MAX_RECORDS_COMMIT = 10   # Number of records to insert before committing.
# Creates reports parsing JSON output into sqlite3 database for easy analysis.

# The configurations for the database are found in a file 'oclc.yaml' in the
# root of the project directory (the directory above ./lib).
class OclcRpt:
    # Creates the object with settings from oclc.yaml by default.
    def __init__(self, yaml_file:str, debug:bool=False):
        yaml_file = join(dirname(__file__), '..', yaml_file)
        if exists(yaml_file):
            with open(yaml_file) as YAML:
                try:
                    self.configs = yaml.safe_load(YAML)
                    self.db = self.configs['database']['name']
                    self.db_path = self.configs['database']['path']
                    self.add_table = self.configs['database']['add_table_name']
                    self.del_table = self.configs['database']['del_table_name']
                except yaml.YAMLError as exc:
                    sys.stderr.write(f"{exc}")
        else:
            sys.stderr.write(f"*error, yaml file not found! Expected '{yaml_file}'")
            sys.exit()
        self.debug = debug

    # Creates a table in the sqlite3 database with the argument table
    # name and columns provided. 
    # param: table name string, setting found in yaml. 
    # param: columns list of string names of the columns.
    def _create_table_(self, table_name:str, columns:list):
        create_str = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        for i in range(0, len(columns)):
            create_str += f"    {columns[i]} TEXT"
            # Don't put a trailing comma on the last column declaration.
            if i < len(columns) -1:
                create_str += f","
            create_str += f"\n"
        create_str += f")"
        if self.debug:
            print(f"create query: {create_str}")
        db = sqlite3.connect(self.db)
        cursor = db.cursor()
        cursor.execute(f"{create_str}")
        db.commit()
        db.close()

    # Adds a check response to the database. 
    # param: json object check response. 
    # param: action taken on the OCLC database of either 'set', 'unset', or 'check'. 
    # Default 'set'. 
    # return: count integer of records inserted.
    def set_and_check_reponse(self, json_response:dict, action:str='set') -> int:
        records = json_response
        # Expected, and useful columns from web service JSON output.
        columns = ['title', 'requestedOclcNumber', 'currentOclcNumber', 'institution', 'status', 'detail', 'id', 'found', 'merged', 'updated']
        self._create_table_(self.add_table, columns)
        # Insert values from the JSON.
        db = sqlite3.connect(self.db)
        cursor = db.cursor()
        query = f"INSERT INTO {self.add_table} VALUES (?,?,?,?,?,?,?,?,?,?)"
        count = 0
        for entry in records['entries']:
            record = {}
            # if self.debug:
            #     print(f"{entry}")
            record['title'] = entry['title']
            c = entry['content']
            record['requestedOclcNumber'] = c['requestedOclcNumber']
            record['currentOclcNumber']= c['currentOclcNumber']
            record['institution'] = c['institution']
            record['status'] = c['status']
            record['detail'] = c['detail']
            record['id'] = c['id']
            record['found'] = c['found'] # Written as '1' true, and '0' False
            record['merged'] = c['merged'] # Written as '1' true, and '0' False
            record['updated'] = entry['updated']
            cursor.execute(query, list(record.values()))
            if count >= MAX_RECORDS_COMMIT:
                db.commit()
            count += 1
        db.commit()
        db.close()
        if self.debug:
            print(f"loaded {count} records.")
        return count

    # Selects all OCLC numbers that are marked missing.
    def report_missing(self):
        pass

if __name__ == "__main__":
    import doctest
    doctest.testfile("oclcrpt.tst")