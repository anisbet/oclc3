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
    """
    >>> marc_slim = MarcXML(["*** DOCUMENT BOUNDARY ***", ".000. |ajm a0c a", ".008. |a111222s2012    nyu||n|j|         | eng d", ".035.   |a(OCoLC)769144454", "*** DOCUMENT BOUNDARY ***"])
    >>> print(marc_slim)
    <?xml version="1.0" encoding="UTF-8"?>
    <record xmlns="http://www.loc.gov/MARC21/slim" >
    <leader>jm a0c a</leader>
    <controlfield tag="008">111222s2012    nyu||n|j|         | eng d</controlfield>
    <datafield tag="035" ind1=" " ind2=" ">
      <subfield code="a">(OCoLC)769144454</subfield>
    </datafield>
    </record>
    >>> marc_std = MarcXML(["*** DOCUMENT BOUNDARY ***", ".000. |ajm a0c a", ".008. |a111222s2012    nyu||n|j|         | eng d", ".035.   |a(OCoLC)769144454", "*** DOCUMENT BOUNDARY ***"], 'standard')
    >>> print(marc_std)
    <?xml version="1.0" encoding="UTF-8"?>
    <record xmlns:marc="http://www.loc.gov/MARC21/slim" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd" >
    <marc:leader>jm a0c a</marc:leader>
    <marc:controlfield tag="008">111222s2012    nyu||n|j|         | eng d</marc:controlfield>
    <marc:datafield tag="035" ind1=" " ind2=" ">
      <marc:subfield code="a">(OCoLC)769144454</marc:subfield>
    </marc:datafield>
    </marc:record>
    """
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
        """
        >>> marc_slim = MarcXML([])
        >>> print(marc_slim._get_tag_(".000. |ajm a0c a"))
        000
        """
        t = re.match(r'\.\d{3}\.', entry)
        if t:
            # print(f"==>{t.group()}")
            t = t.group()[1:-1]
            return f"{t}"
        else:
            return ''

    def _get_control_field_data_(self, entry:str, raw:bool=True) -> str:
        """
        >>> marc_slim = MarcXML([])
        >>> print(marc_slim._get_control_field_data_(".000. |ajm a0c a"))
        |ajm a0c a
        """
        fields = entry.split('|a')
        if raw:
            return f"|a{fields[1]}"
        return f"{fields[1]}"
    
    def _get_indicators_(self, entry:str) -> list:
        """
        >>> marc_slim = MarcXML([])
        >>> print(f"{marc_slim._get_indicators_('.082. 04|a782.42/083|223')}")
        ('0', '4')
        >>> print(f"{marc_slim._get_indicators_('.082.   |a782.42/083|223')}")
        (' ', ' ')
        >>> print(f"{marc_slim._get_indicators_('.082. 1 |a782.42/083|223')}")
        ('1', ' ')
        >>> print(f"{marc_slim._get_indicators_('.082.  5|a782.42/083|223')}")
        (' ', '5')
        >>> print(f"{marc_slim._get_indicators_('.050.  4|aM1997.F6384|bF47 2012')}")
        (' ', '4')
        """
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


    def _get_subfields_(self, entry:str) -> list:
        """
        >>> marc_slim = MarcXML([])
        >>> print(f"{marc_slim._get_subfields_('.040.   |aTEFMT|cTEFMT|dTEF|dBKX|dEHH|dNYP|dUtOrBLW')}")
        ['<datafield tag="040" ind1=" " ind2=" ">', '  <subfield code="a">TEFMT</subfield>', '  <subfield code="c">TEFMT</subfield>', '  <subfield code="d">TEF</subfield>', '  <subfield code="d">BKX</subfield>', '  <subfield code="d">EHH</subfield>', '  <subfield code="d">NYP</subfield>', '  <subfield code="d">UtOrBLW</subfield>', '</datafield>']
        >>> print(f"{marc_slim._get_subfields_('.050.  4|aM1997.F6384|bF47 2012')}")
        ['<datafield tag="050" ind1=" " ind2="4">', '  <subfield code="a">M1997.F6384</subfield>', '  <subfield code="b">F47 2012</subfield>', '</datafield>']
        """
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

    def _convert_(self, entries:list):
        """
        >>> marc_slim = MarcXML([
        ... "*** DOCUMENT BOUNDARY ***",
        ... "FORM=MUSIC",
        ... ".000. |ajm a0c a",
        ... ".001. |aocn769144454",
        ... ".003. |aOCoLC",
        ... ".005. |a20140415031111.0",
        ... ".007. |asd fsngnnmmned",
        ... ".008. |a111222s2012    nyu||n|j|         | eng d",
        ... ".024. 1 |a886979578425",
        ... ".028. 00|a88697957842",
        ... ".035.   |a(Sirsi) a1001499",
        ... ".035.   |a(Sirsi) a1001499",
        ... ".035.   |a(OCoLC)769144454",
        ... ".035.   |a(CaAE) a1001499",
        ... ".040.   |aTEFMT|cTEFMT|dTEF|dBKX|dEHH|dNYP|dUtOrBLW"])
        >>> print(marc_slim)
        <?xml version="1.0" encoding="UTF-8"?>
        <record xmlns="http://www.loc.gov/MARC21/slim" >
        <leader>jm a0c a</leader>
        <controlfield tag="001">ocn769144454</controlfield>
        <controlfield tag="003">OCoLC</controlfield>
        <controlfield tag="005">20140415031111.0</controlfield>
        <controlfield tag="007">sd fsngnnmmned</controlfield>
        <controlfield tag="008">111222s2012    nyu||n|j|         | eng d</controlfield>
        <datafield tag="024" ind1="1" ind2=" ">
          <subfield code="a">886979578425</subfield>
        </datafield>
        <datafield tag="028" ind1="0" ind2="0">
          <subfield code="a">88697957842</subfield>
        </datafield>
        <datafield tag="035" ind1=" " ind2=" ">
          <subfield code="a">(Sirsi) a1001499</subfield>
        </datafield>
        <datafield tag="035" ind1=" " ind2=" ">
          <subfield code="a">(Sirsi) a1001499</subfield>
        </datafield>
        <datafield tag="035" ind1=" " ind2=" ">
          <subfield code="a">(OCoLC)769144454</subfield>
        </datafield>
        <datafield tag="035" ind1=" " ind2=" ">
          <subfield code="a">(CaAE) a1001499</subfield>
        </datafield>
        <datafield tag="040" ind1=" " ind2=" ">
          <subfield code="a">TEFMT</subfield>
          <subfield code="c">TEFMT</subfield>
          <subfield code="d">TEF</subfield>
          <subfield code="d">BKX</subfield>
          <subfield code="d">EHH</subfield>
          <subfield code="d">NYP</subfield>
          <subfield code="d">UtOrBLW</subfield>
        </datafield>
        </record>
        """
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
    doctest.testmod()
# EOF