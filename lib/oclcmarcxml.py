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
class MarcRecord:
    def __init__(self, flat:list):
        pass

    def __str__(self):
        pass

class MarcXML:
    """
    >>> m = MarcXML(["*** DOCUMENT BOUNDARY ***", ".000. |ajm a0c a", "*** DOCUMENT BOUNDARY ***"])
    >>> print(m)
    <?xml version="1.0" encoding="UTF-8"?><record xmlns="http://www.loc.gov/MARC21/slim"><leader>jm a0c a</leader></record>
    """
    def __init__(self, flat:list):
        rs = re.compile(r'\*\*\* DOCUMENT BOUNDARY \*\*\*')
        self.xml = []
        # Add declaration.
        self.xml.append('<?xml version="1.0" encoding="UTF-8"?>')
        record = []
        while len(flat) > 0:
            line = flat.pop()
            if rs.match(line):
                # print(f"found: record start")
                if len(record) > 0:
                    record.append('</record>')
                    self.xml.append(record)
                record = []
                if len(flat) > 0:
                    record.append('<record xmlns="http://www.loc.gov/MARC21/slim">')
            else:
                record.append(self._convert_(line))

    # Gets a string version of the entry's tag, like '000' or '035'.
    # param: str of the flat entry from the flat marc data.
    # return: str of the tag or empty string if no tag was found.
    def _get_tag_(self, entry:str) -> str:
        """
        >>> m = MarcXML([])
        >>> print(m._get_tag_(".000. |ajm a0c a"))
        000
        """
        t = re.match(r'\.\d{3}\.', entry)
        if t:
            # print(f"==>{t.group()}")
            t = t.group()[1:-1]
            return f"{t}"
        else:
            return ''

    def _get_fields_(self, entry:str, raw:bool=True) -> str:
        """
        >>> m = MarcXML([])
        >>> print(m._get_fields_(".000. |ajm a0c a"))
        |ajm a0c a
        """
        fields = entry.split('|a')
        if raw:
            return f"|a{fields[1]}"
        return f"{fields[1]}"
    
    def _get_indicators_(self, entry:str) -> list:
        """
        >>> m = MarcXML([])
        >>> print(f"{m._get_indicators_('.082. 04|a782.42/083|223')}")
        ('0', '4')
        >>> print(f"{m._get_indicators_('.082.   |a782.42/083|223')}")
        (' ', ' ')
        >>> print(f"{m._get_indicators_('.082. 1 |a782.42/083|223')}")
        ('1', ' ')
        >>> print(f"{m._get_indicators_('.082.  5|a782.42/083|223')}")
        (' ', '5')
        >>> print(f"{m._get_indicators_('.050.  4|aM1997.F6384|bF47 2012')}")
        (' ', '4')
        """
        # .245. 04|aThe Fresh Beat Band|h[sound recording] :|bmusic from the hit TV show.
        inds = entry.split('|a')
        ind1 = ' '
        ind2 = ' '
        if inds:
            ind1 = inds[0][-2:][0]
            ind2 = inds[0][-2:][1]
        return (ind1,ind2)


    def _get_subfields_(self, entry:str) -> str:
        """
        >>> m = MarcXML([])
        >>> print(f"{m._get_subfields_('.040.   |aTEFMT|cTEFMT|dTEF|dBKX|dEHH|dNYP|dUtOrBLW')}")
        <datafield tag="040" ind1=" " ind2=" ">
          <subfield code="a">TEFMT</subfield>
          <subfield code="c">TEFMT</subfield>
          <subfield code="d">TEF</subfield>
          <subfield code="d">BKX</subfield>
          <subfield code="d">EHH</subfield>
          <subfield code="d">NYP</subfield>
          <subfield code="d">UtOrBLW</subfield>
        </datafield>
        >>> print(f"{m._get_subfields_('.050.  4|aM1997.F6384|bF47 2012')}")
        <datafield tag="050" ind1=" " ind2="4">
          <subfield code="a">M1997.F6384</subfield>
          <subfield code="b">F47 2012</subfield>
        </datafield>
        """
        # Given: '.040.  1 |aTEFMT|cTEFMT|dTEF|dBKX|dEHH|dNYP|dUtOrBLW'
        tag           = self._get_tag_(entry)        # '040'
        (ind1, ind2)  = self._get_indicators_(entry) # ('1',' ')
        data_fields   = self._get_fields_(entry)     # '|aTEFMT|cTEFMT|dTEF|dBKX|dEHH|dNYP|dUtOrBLW'
        subfields     = data_fields.split('|')
        subfield_list = []
        for subfield in subfields:
            # The sub field name is the first character
            field_name = subfield[:1]
            field_value= subfield[1:]
            if field_name != '':
                subfield_list.append((field_name, field_value))
        
        tag_entries = [f"<datafield tag=\"{tag}\" ind1=\"{ind1}\" ind2=\"{ind2}\">"]
        for subfield in subfield_list:
            # ['TEFMT', ('c', 'TEFMT'), ('d', 'TEF'), ('d', 'BKX'), ('d', 'EHH'), ('d', 'NYP'), ('d', 'UtOrBLW')]
            tag_entries.append(f"  <subfield code=\"{subfield[0]}\">{subfield[1]}</subfield>")
        tag_entries.append(f"</datafield>")
        return '\n'.join(tag_entries)

    def _convert_(self, flat:str):
        # .000. |ajm a0c a
        # .001. |aocn769144454
        # .003. |aOCoLC
        # .005. |a20140415031111.0
        # .007. |asd fsngnnmmned
        # .008. |a111222s2012    nyu||n|j|         | eng d
        # .024. 1 |a886979578425
        # .028. 00|a88697957842
        # .035.   |a(Sirsi) a1001499
        # .035.   |a(Sirsi) a1001499
        # .035.   |a(OCoLC)769144454
        # .035.   |a(CaAE) a1001499
        # .040.   |aTEFMT|cTEFMT|dTEF|dBKX|dEHH|dNYP|dUtOrBLW
        record = []
        tag = self._get_tag_(flat)
        if tag == '000':
            record.append(f"<leader>{self._get_fields_(flat, False)}</leader>")
        elif tag == '008':
            record.append(f"<controlfield tag=\"{tag}\">{self._get_fields_(flat, False)}</controlfield>")
        elif tag == '':
            pass # Not sure, perhaps a run-on sentence from flatskip.
        else:
            record.append(self._get_subfields_(flat))

        # <marc_field tag="250" label="Edition">ON ORDER</marc_field>
        return '\n'.join(record)

    def __str__(self) -> str:
        return str.join('', [item for sublist in self.xml for item in sublist])


if __name__ == "__main__":
    import doctest
    doctest.testmod()
# EOF