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
import os
import sqlite3

DEFAULT_DB_NAME = 'test.db'
MAX_RECORDS_COMMIT = 500   # Number of records to insert before committing.
# Creates reports parsing JSON output into sqlite3 database for easy analysis.
class OclcRpt:

    def __init__(self, db_name:str='', debug:bool=False):
        self.db_name = DEFAULT_DB_NAME
        self.debug = debug
        if db_name != '' and db_name != None:
            self.db_name = db_name

    def _create_table_(self, columns:list, table_name:str):
        """
        >>> o = OclcRpt('test00.db', True)
        >>> cols = ['a','b','c']
        >>> o._create_table_(cols, 'test')
        create query: CREATE TABLE IF NOT EXISTS test (
            a TEXT,
            b TEXT,
            c TEXT
        )
        >>> os.remove('test00.db')
        """
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
        db = sqlite3.connect(self.db_name)
        cursor = db.cursor()
        cursor.execute(f"{create_str}")
        db.commit()
        db.close()

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
    #     }, 
    #     {"title": "850939596", 
    #         "content": {
    #             "requestedOclcNumber": "850939596", 
    #             "currentOclcNumber": "850939596", 
    #             "institution": "OCPSB", "status": "HTTP 200 OK", "detail": "Record found.", 
    #             "id": "http://worldcat.org/oclc/850939596", 
    #             "found": true, 
    #             "merged": False
    #         }, 
    #         "updated": "2023-01-31T20:39:40.089Z"
    #     }]
    # }
    def db_load_get_holdings_results(self, json_data:dict, table_name:str='oclc'):
        """
        >>> d={"entries":[{"title":"850939592","content":{"requestedOclcNumber":"850939592","currentOclcNumber":"850939592","institution":"OCPSB","status":"HTTP 200 OK","detail":"Record found.","id":"http://worldcat.org/oclc/850939592","found":True,"merged":False},"updated":"2023-01-31T20:39:40.088Z"},{"title":"850939596","content":{"requestedOclcNumber":"850939596","currentOclcNumber":"850939596","institution":"OCPSB","status":"HTTP 200 OK","detail":"Record found.","id":"http://worldcat.org/oclc/850939596","found":True,"merged":False},"updated":"2023-01-31T20:39:40.089Z"}]}
        >>> o = OclcRpt('test00.db', True)
        >>> o.db_load_get_holdings_results(d, 'test')
        create query: CREATE TABLE IF NOT EXISTS test (
            title TEXT,
            requestedOclcNumber TEXT,
            currentOclcNumber TEXT,
            institution TEXT,
            status TEXT,
            detail TEXT,
            id TEXT,
            found TEXT,
            merged TEXT,
            updated TEXT
        )
        loaded 2 records.
        """
        records = json_data
        # Expected, and useful columns from web service JSON output.
        columns = ['title', 'requestedOclcNumber', 'currentOclcNumber', 'institution', 'status', 'detail', 'id', 'found', 'merged', 'updated']
        self._create_table_(columns, table_name)
        # Insert values from the JSON.
        db = sqlite3.connect(self.db_name)
        cursor = db.cursor()
        query = f"INSERT INTO {table_name} VALUES (?,?,?,?,?,?,?,?,?,?)"
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

    # Selects all OCLC numbers that are marked missing.
    def report_missing(self):
        pass

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    # EOF