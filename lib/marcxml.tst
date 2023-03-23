
Test flat to marc 21 xml conversions.
-------------------------------------

Basic imports

	>>> from flat2marcxml import MarcXML

Test the tag getting function
-----------------------------


	>>> marc_slim = MarcXML([])
	>>> marc_slim._get_tag_(".000. |ajm a0c a")
	'000'

	>>> marc_slim = MarcXML([])
	>>> marc_slim._get_control_field_data_(".000. |ajm a0c a")
	'|ajm a0c a'


Test get indicators
-------------------

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


Test get subfields
------------------


	>>> marc_slim = MarcXML([])
	>>> print(f"{marc_slim._get_subfields_('.040.   |aTEFMT|cTEFMT|dTEF|dBKX|dEHH|dNYP|dUtOrBLW')}")
	['<datafield tag="040" ind1=" " ind2=" ">', '  <subfield code="a">TEFMT</subfield>', '  <subfield code="c">TEFMT</subfield>', '  <subfield code="d">TEF</subfield>', '  <subfield code="d">BKX</subfield>', '  <subfield code="d">EHH</subfield>', '  <subfield code="d">NYP</subfield>', '  <subfield code="d">UtOrBLW</subfield>', '</datafield>']
	>>> print(f"{marc_slim._get_subfields_('.050.  4|aM1997.F6384|bF47 2012')}")
	['<datafield tag="050" ind1=" " ind2="4">', '  <subfield code="a">M1997.F6384</subfield>', '  <subfield code="b">F47 2012</subfield>', '</datafield>']
	>>> print(f"{marc_slim._get_subfields_('.245.  4|aTreasure Island, 2004')}")
	['<datafield tag="245" ind1=" " ind2="4">', '  <subfield code="a">Treasure Island, 2004</subfield>', '</datafield>']


Test XML production from slim FLAT data.
---------------------------------------


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


Test standard namespace marc XML production
-----------------------------


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


Test convert method
-------------------


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
