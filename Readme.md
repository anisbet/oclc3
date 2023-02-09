# OCLC Holdings Management

oclc is a Python application to update OCLC local library holdings.

## Installation

* Clone the project [GitHub](https://github.com/anisbet) a clean folder.
* Make sure python 3.7 (minimum) is installed.
* Create a YAML of you site's [OCLC settngs](#required-oclc-settings).
* TODO: are there libs to intall? If so create a requirements doc.
* Run as follows.
* After testing schedule.

```bash
python oclc.py
```
## Required OCLC Settings
This is a comprehensive list of all the settings you will need to manage local holdings. Please contact [OCLC Developer Network APIs](https://www.oclc.org/developer/develop/web-services.en.html) for more information.

## Usage


## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[Apache2](https://choosealicense.com/licenses/apache-2.0/)

# Complete Mixed selection shell commands
That is titles that have been modified (-r) or created (-p) since 90-days ago.
```bash
selitem -t"~PAPERBACK,JPAPERBACK,BKCLUBKIT,COMIC,DAISYRD,EQUIPMENT,E-RESOURCE,FLICKSTOGO,FLICKTUNE,JFLICKTUNE,JTUNESTOGO,PAMPHLET,RFIDSCANNR,TUNESTOGO,JFLICKTOGO,PROGRAMKIT,LAPTOP,BESTSELLER,JBESTSELLR" -l"~BARCGRAVE,CANC_ORDER,DISCARD,EPLACQ,EPLBINDERY,EPLCATALOG,EPLILL,INCOMPLETE,LONGOVRDUE,LOST,LOST-ASSUM,LOST-CLAIM,LOST-PAID,MISSING,NON-ORDER,BINDERY,CATALOGING,COMICBOOK,INTERNET,PAMPHLET,DAMAGE,UNKNOWN,REF-ORDER,BESTSELLER,JBESTSELLR,STOLEN" -oC 2>/dev/null | sort | uniq >catkeys.no_t.no_l.lst 
cat catkeys.no_t.no_l.lst | selcatalog -iC -p">`transdate -d-90`" -oC  >mixed.catkeys.90d.lst
cat catkeys.no_t.no_l.lst | selcatalog -iC -r">`transdate -d-90`" -oC  >>mixed.catkeys.90d.lst 
cat mixed.catkeys.90d.lst | sort | uniq >mixed.catkeys.90d.uniq.lst
cat mixed.catkeys.90d.uniq.lst | catalogdump -kf035 -of | grep -v -i -e '\.250\.[ \t]+\|aExpected release' >flat.wo.onorder.lst
cat flat.wo.onorder.lst | flatskip -if -aMARC -om >mixed.mrc
```

# XML Reference
Ref
* [https://www.loc.gov/standards/marcxml](https://www.loc.gov/standards/marcxml)
* [https://www.loc.gov/standards/marcxml/xml/spy/spy.html](https://www.loc.gov/standards/marcxml/xml/spy/spy.html) 
* [https://www.loc.gov/standards/marcxml/xml/collection.xml](https://www.loc.gov/standards/marcxml/xml/collection.xml) 
## Schema
* [https://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd](https://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd)

##
This tool outputs catalog information about items, as an example:
```bash
head mixed.catkeys.90d.lst | xmlitem -iC -cf -e035,008,250 # Other tags can be added.
```
### LOC MARC XML Full Example
From Library of Congress [https://www.loc.gov/standards/marcxml/xml/collection.xml](https://www.loc.gov/standards/marcxml/xml/collection.xml)

```xml
<marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd">
<marc:record>
<marc:leader>00925njm 22002777a 4500</marc:leader>
<marc:controlfield tag="001">5637241</marc:controlfield>
<marc:controlfield tag="003">DLC</marc:controlfield>
<marc:controlfield tag="005">19920826084036.0</marc:controlfield>
<marc:controlfield tag="007">sdubumennmplu</marc:controlfield>
<marc:controlfield tag="008">910926s1957 nyuuun eng </marc:controlfield>
<marc:datafield tag="010" ind1=" " ind2=" ">
<marc:subfield code="a"> 91758335 </marc:subfield>
</marc:datafield>
<marc:datafield tag="028" ind1="0" ind2="0">
<marc:subfield code="a">1259</marc:subfield>
<marc:subfield code="b">Atlantic</marc:subfield>
</marc:datafield>
<marc:datafield tag="040" ind1=" " ind2=" ">
<marc:subfield code="a">DLC</marc:subfield>
<marc:subfield code="c">DLC</marc:subfield>
</marc:datafield>
<marc:datafield tag="050" ind1="0" ind2="0">
<marc:subfield code="a">Atlantic 1259</marc:subfield>
</marc:datafield>
<marc:datafield tag="245" ind1="0" ind2="4">
<marc:subfield code="a">The Great Ray Charles</marc:subfield>
<marc:subfield code="h">[sound recording].</marc:subfield>
</marc:datafield>
<marc:datafield tag="260" ind1=" " ind2=" ">
<marc:subfield code="a">New York, N.Y. :</marc:subfield>
<marc:subfield code="b">Atlantic,</marc:subfield>
<marc:subfield code="c">[1957?]</marc:subfield>
</marc:datafield>
<marc:datafield tag="300" ind1=" " ind2=" ">
<marc:subfield code="a">1 sound disc :</marc:subfield>
<marc:subfield code="b">analog, 33 1/3 rpm ;</marc:subfield>
<marc:subfield code="c">12 in.</marc:subfield>
</marc:datafield>
<marc:datafield tag="511" ind1="0" ind2=" ">
<marc:subfield code="a">Ray Charles, piano & celeste.</marc:subfield>
</marc:datafield>
<marc:datafield tag="505" ind1="0" ind2=" ">
<marc:subfield code="a">The Ray -- My melancholy baby -- Black coffee -- There's no you -- Doodlin' -- Sweet sixteen bars -- I surrender dear -- Undecided.</marc:subfield>
</marc:datafield>
<marc:datafield tag="500" ind1=" " ind2=" ">
<marc:subfield code="a">Brief record.</marc:subfield>
</marc:datafield>
<marc:datafield tag="650" ind1=" " ind2="0">
<marc:subfield code="a">Jazz</marc:subfield>
<marc:subfield code="y">1951-1960.</marc:subfield>
</marc:datafield>
<marc:datafield tag="650" ind1=" " ind2="0">
<marc:subfield code="a">Piano with jazz ensemble.</marc:subfield>
</marc:datafield>
<marc:datafield tag="700" ind1="1" ind2=" ">
<marc:subfield code="a">Charles, Ray,</marc:subfield>
<marc:subfield code="d">1930-</marc:subfield>
<marc:subfield code="4">prf</marc:subfield>
</marc:datafield>
</marc:record>
</marc:collection>
```

### LOC MARC XML Slim Example
From Library of Congress [https://www.loc.gov/standards/marcxml//Sandburg/sandburg.xml](https://www.loc.gov/standards/marcxml//Sandburg/sandburg.xml)
```xml
<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
<leader>01142cam 2200301 a 4500</leader>
<controlfield tag="001"> 92005291 </controlfield>
<controlfield tag="003">DLC</controlfield>
<controlfield tag="005">19930521155141.9</controlfield>
<controlfield tag="008">920219s1993 caua j 000 0 eng </controlfield>
<datafield tag="010" ind1=" " ind2=" ">
<subfield code="a"> 92005291 </subfield>
</datafield>
<datafield tag="020" ind1=" " ind2=" ">
<subfield code="a">0152038655 :</subfield>
<subfield code="c">$15.95</subfield>
</datafield>
<datafield tag="040" ind1=" " ind2=" ">
<subfield code="a">DLC</subfield>
<subfield code="c">DLC</subfield>
<subfield code="d">DLC</subfield>
</datafield>
<datafield tag="042" ind1=" " ind2=" ">
<subfield code="a">lcac</subfield>
</datafield>
<datafield tag="050" ind1="0" ind2="0">
<subfield code="a">PS3537.A618</subfield>
<subfield code="b">A88 1993</subfield>
</datafield>
<datafield tag="082" ind1="0" ind2="0">
<subfield code="a">811/.52</subfield>
<subfield code="2">20</subfield>
</datafield>
<datafield tag="100" ind1="1" ind2=" ">
<subfield code="a">Sandburg, Carl,</subfield>
<subfield code="d">1878-1967.</subfield>
</datafield>
<datafield tag="245" ind1="1" ind2="0">
<subfield code="a">Arithmetic /</subfield>
<subfield code="c">Carl Sandburg ; illustrated as an anamorphic adventure by Ted Rand.</subfield>
</datafield>
<datafield tag="250" ind1=" " ind2=" ">
<subfield code="a">1st ed.</subfield>
</datafield>
<datafield tag="260" ind1=" " ind2=" ">
<subfield code="a">San Diego :</subfield>
<subfield code="b">Harcourt Brace Jovanovich,</subfield>
<subfield code="c">c1993.</subfield>
</datafield>
<datafield tag="300" ind1=" " ind2=" ">
<subfield code="a">1 v. (unpaged) :</subfield>
<subfield code="b">ill. (some col.) ;</subfield>
<subfield code="c">26 cm.</subfield>
</datafield>
<datafield tag="500" ind1=" " ind2=" ">
<subfield code="a">One Mylar sheet included in pocket.</subfield>
</datafield>
<datafield tag="520" ind1=" " ind2=" ">
<subfield code="a">A poem about numbers and their characteristics. Features anamorphic, or distorted, drawings which can be restored to normal by viewing from a particular angle or by viewing the image's reflection in the provided Mylar cone.</subfield>
</datafield>
<datafield tag="650" ind1=" " ind2="0">
<subfield code="a">Arithmetic</subfield>
<subfield code="x">Juvenile poetry.</subfield>
</datafield>
<datafield tag="650" ind1=" " ind2="0">
<subfield code="a">Children's poetry, American.</subfield>
</datafield>
<datafield tag="650" ind1=" " ind2="1">
<subfield code="a">Arithmetic</subfield>
<subfield code="x">Poetry.</subfield>
</datafield>
<datafield tag="650" ind1=" " ind2="1">
<subfield code="a">American poetry.</subfield>
</datafield>
<datafield tag="650" ind1=" " ind2="1">
<subfield code="a">Visual perception.</subfield>
</datafield>
<datafield tag="700" ind1="1" ind2=" ">
<subfield code="a">Rand, Ted,</subfield>
<subfield code="e">ill.</subfield>
</datafield>
</record>
</collection>
```

### OCLC MARC XML example
Compare to OCLC well formed submission:
```xml
<?xml version="1.0" encoding="UTF-8"?> <record xmlns="http://www.loc.gov/MARC21/slim">
    <leader>00000nam a2200000 a 4500</leader>
    <controlfield tag="008">120827s2012    nyua          000 0 eng d</controlfield>
    <datafield tag="010" ind1=" " ind2=" ">
        <subfield code="a">   63011276 </subfield>
    </datafield>
    <datafield tag="040" ind1=" " ind2=" ">
        <subfield code="a">OCWMS</subfield>
        <subfield code="b">eng</subfield>
        <subfield code="c">OCPSB</subfield>
    </datafield>
    <datafield tag="100" ind1="0" ind2=" ">
        <subfield code="a">OCLC Developer Network</subfield>
    </datafield>
    <datafield tag="245" ind1="1" ind2="0">
        <subfield code="a">Test Record</subfield>
    </datafield>
    <datafield tag="500" ind1=" " ind2=" ">
        <subfield code="a">FOR OCLC DEVELOPER NETWORK DOCUMENTATION</subfield>
    </datafield>
</record> 
```