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
import re
###
# This class formats flat data into MARC XML either as described by the Library
# of Congress with specific considerations for the expectation of OCLC.
# Ref: 
#   https://www.loc.gov/standards/marcxml/
#   https://www.loc.gov/standards/marcxml/xml/spy/spy.html 
#   https://www.loc.gov/standards/marcxml/xml/collection.xml
# Schema:
#   https://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd

class MarcXML:
    def __init__(self, flat:list, namespace:str='slim'):
        new_doc = re.compile(r'\*\*\* DOCUMENT BOUNDARY \*\*\*')
        self.xml = []
        slim = ''
        slim_ns = """xmlns="http://www.loc.gov/MARC21/slim" """
        std = 'marc:'
        std_ns = """xmlns:marc="http://www.loc.gov/MARC21/slim" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd" """
        self.prefix = slim
        self.ns = slim_ns
        if namespace == 'standard':
            self.prefix = std
            self.ns = std_ns
        # Add declaration.
        self.xml.append(f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
        record = []
        while flat:
            line = flat.pop()
            if new_doc.match(line):
                if record:
                    record.reverse()
                    self.xml.append(self._convert_(record))
                record = []
            else:
                record.append(line)
        if record:
            record.reverse()
            self.xml.append(self._convert_(record))

    # Gets a string version of the entry's tag, like '000' or '035'.
    # param: str of the flat entry from the flat marc data.
    # return: str of the tag or empty string if no tag was found.
    def _get_tag_(self, entry:str) -> str:
        t = re.match(r'\.\d{3}\.', entry)
        if t:
            # print(f"==>{t.group()}")
            t = t.group()[1:-1]
            return f"{t}"
        else:
            return ''

    def _get_control_field_data_(self, entry:str, raw:bool=True) -> str:
        fields = entry.split('|a')
        if raw:
            return f"|a{fields[1]}"
        return f"{fields[1]}"
    
    def _get_indicators_(self, entry:str) -> list:
        # .245. 04|aThe Fresh Beat Band|h[sound recording] :|bmusic from the hit TV show.
        inds = entry.split('|a')
        ind1 = ' '
        ind2 = ' '
        # There are no indicators for fields < '008'.
        tag = self._get_tag_(entry)
        if inds and int(tag) >= 8:
            ind1 = inds[0][-2:][0]
            ind2 = inds[0][-2:][1]
        return (ind1,ind2)

    # Private method that, given a MARC field returns 
    # a list of any subfields.
    def _get_subfields_(self, entry:str) -> list:
        # Given: '.040.  1 |aTEFMT|cTEFMT|dTEF|dBKX|dEHH|dNYP|dUtOrBLW'
        tag           = self._get_tag_(entry)        # '040'
        (ind1, ind2)  = self._get_indicators_(entry) # ('1',' ')
        tag_entries   = [f"<{self.prefix}datafield tag=\"{tag}\" ind1=\"{ind1}\" ind2=\"{ind2}\">"]
        data_fields   = self._get_control_field_data_(entry)     # '|aTEFMT|cTEFMT|dTEF|dBKX|dEHH|dNYP|dUtOrBLW'
        subfields     = data_fields.split('|')
        subfield_list = []
        for subfield in subfields:
            # The sub field name is the first character
            field_name = subfield[:1]
            field_value= subfield[1:]
            if field_name != '':
                subfield_list.append((field_name, field_value))
        for subfield in subfield_list:
            # [('a', 'TEFMT'), ('c', 'TEFMT'), ('d', 'TEF'), ('d', 'BKX'), ('d', 'EHH'), ('d', 'NYP'), ('d', 'UtOrBLW')]
            tag_entries.append(f"  <{self.prefix}subfield code=\"{subfield[0]}\">{subfield[1]}</{self.prefix}subfield>")
        tag_entries.append(f"</{self.prefix}datafield>")
        return tag_entries

    # Converts MARC tag entries into XML. 
    # param: entries list of FLAT data strings.
    # return: list of XML strings.
    def _convert_(self, entries:list) ->list:
        record = []
        if entries:
            record.append(f"<record {self.ns}>")
        for entry in entries:
            # Sirsi Dynix flat files contain a 'FORM=blah-blah' which is not valid MARC.
            if re.match(r'^FORM*', entry):
                continue
            tag = self._get_tag_(entry)
            if tag == '000':
                record.append(f"<{self.prefix}leader>{self._get_control_field_data_(entry, False)}</{self.prefix}leader>")
            # Any tag below '008' is a control field and doesn't have indicators or subfields.
            elif int(tag) <= 8:
                record.append(f"<{self.prefix}controlfield tag=\"{tag}\">{self._get_control_field_data_(entry, False)}</{self.prefix}controlfield>")
            else:
                record.append(self._get_subfields_(entry))
        if entries:
            record.append(f"</{self.prefix}record>")
        return record

    # Used to collapse lists within lists, for example when printing the xml as a string.
    def _flatten_(self, final_list:list, lst):
        for item in lst:
            if isinstance(item, list):
                self._flatten_(final_list, item)
            else:
                final_list.append(item)
    
    def __str__(self) -> str:
        a = []
        self._flatten_(a, self.xml)
        return '\n'.join(a)


if __name__ == "__main__":
    import doctest
    doctest.testfile("marcxml.tst")
# EOF