# OCLC Holdings Management

`oclc` is a Python application to manage library holdings in OCLC's [WorldCat discovery](https://www.worldcat.org/) database through [WorldCat Metadata web services](https://www.oclc.org/developer/develop/web-services.en.html). [See here for more information](#regular-worldcat-maintenance).

## Testing
The application is controlled by a YAML file which contains the following values.
```yaml
# Setting oclc3 uses.
service: 
  name:          'WCMetaDataTest'
  clientId:      'some_long_hex_string'
  secret:        'p@ssW0rD!_or_something stronger'
  registryId:    '128807' # Test registry ID supplied by OCLC.
  principalId:   'a_long_hash_string_identifier' # Provided but not used.
  principalIdns: 'urn:oclc:wms:da' # Provided but not used.
  institutionalSymbol: 'OCPSB' # Test institutional symbol supplied by OCLC.

# Configurations for the database.
database:
  name: 'oclc.db'
  path: '..'   # Location of the database file relative to the 'lib/' directory.
  add_table_name: 'added' # Table name
  del_table_name: 'deleted' # Table name - can be (almost) anything you like.
```

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

## Regular WorldCat Maintenance
OCLC is a consortium that offers online catalog discovery tools for academic, public, and special libraries. Each library that pays for the service will appear as a holding library for title searches world-wide. 

To support this OCLC maintains a huge catalog of titles contributed by members. But to reduce redundancy of every library submitting a record for 'Treasure Island', they have just one well-formed record, and each library indicates they have the title by marking the record as a *holding* under their institution ID. This is known as **setting** the holding. Once set the library will appear as one of the lending locations for the title in world-wide searches.

If the library weeds the title from their collection they update OCLC by **unsetting** the title. Once done the library no longer appears as a holding library.

Any unique title the library possesses can be uploaded as a *local holding* by submitting their catalog record(s) as MARC21 XML.

The **oclc3.py** script allows for the maintenance of holdings at OCLC by supporting each of these functions.
1) Setting holdings - which, when using the old batch process, where known as *updates* and *creates*.
2) Unsetting holdings - Also known as *deletes* in batch processing.
3) Local Holdings Submission - Previously this was simply covered by the *creates* and *updates* in the batch process.

# Reclamations Instructions
As mentioned before, records were maintained at OCLC through a batch process which consisted of collecting all new and updated records of interest and submitting slim MARC records to OCLC. Deletes were handled by searching the ILS logs for remove title commands which is the only surviving evidence of a purged title in the ILS. Typically the search starts from the last time the batch ran, remove title commands may be missed if they occurred outside of the search time-frame window. 

The result is sometimes titles didn't get unset, and customers would get upset that the library indicates they have the title but they don't. 

To fix the mismatch of library's holdings OCLC offers a **reclamation** service. At the library's request and a cost of a few thousands of dollars, OCLC will purge all the holdings for a library and the library submits a complete new set.

To remediate this expense and improve customer service ```oclc3``` can run a reclamation process.

## OCLC Records
1) Create a report of all the titles from the library by logging into OCLC's [WorldShare Administration Portal](https://edmontonpl.share.worldcat.org/wms/cmnd/analytics/myLibrary).
2) Once logged in select the ```Analytics``` tab.
3) Select Collection Evaluation and click the ```My Library``` button.
4) Below the summary table select export title list, and dismiss the dialog telling you how long it will take. Expect at least 1.5 hours.
5) Download the zipped XSL file from the ```My Files``` menu on the left of the page.
6) Use ```pandas``` or ```excel``` to open and analyse. Expect trouble because there are half a million entries, some with columns of hundreds of characters.
**Hint**:
   1) Open the ```CSV``` in ```OpenOffice``` sheets as a fixed width document.
   2) Save as ```full_cat.csv```.
   3) Use ```cat full_cat.csv | awk -F'""' '{print $4}' >oclcnumbers.txt``` to capture all the OCLC numbers.
1) Select all the OCLC numbers from your library's catalog with API. Typically selection is restricted to titles that you want to appear in WorldCat searches; not electronic resources, internet databases, or non-circulating items. See [this section](#library-records) for example instructions for a SirsiDynix Symphony ILS.

## Library Records
```bash
selitem \ 
-t"~PAPERBACK,JPAPERBACK,BKCLUBKIT,COMIC,DAISYRD,EQUIPMENT,E-RESOURCE,FLICKSTOGO,FLICKTUNE,JFLICKTUNE,JTUNESTOGO,PAMPHLET,RFIDSCANNR,TUNESTOGO,JFLICKTOGO,PROGRAMKIT,LAPTOP,BESTSELLER,JBESTSELLR" \ 
-l"~BARCGRAVE,CANC_ORDER,DISCARD,EPLACQ,EPLBINDERY,EPLCATALOG,EPLILL,INCOMPLETE,LONGOVRDUE,LOST,LOST-ASSUM,LOST-CLAIM,LOST-PAID,MISSING,NON-ORDER,BINDERY,CATALOGING,COMICBOOK,INTERNET,PAMPHLET,DAMAGE,UNKNOWN,REF-ORDER,BESTSELLER,JBESTSELLR,STOLEN" \ 
-oC 2>/dev/null | sort | uniq >catkeys.wo_types.wo_locations.lst 
cat catkeys.wo_types.wo_locations.lst | catalogdump -kf035 -of | nowrap.pl | grep -v -i -e '\.250\.[ \t]+\|aExpected release' >all_records.flat
# We'll use the flat file later to make any XML required to add records if needed.
awk -F"\|a" '{ if ($2 ~ /\(OCoLC\)/) { oclcnum = $2; gsub(/\(OCoLC\)/, "", oclcnum); print oclcnum; }}' all_records.flat >librarynumbers.txt
```

Once done use ```oclc3.py``` script's **TODO: which switch??** can be used to create a master list of OCLC numbers. Those marked with `+` need to be set, those with `-` need to be unset, and a ` ` indicates nothing needs to be done.

## Complete Mixed selection shell commands
That is titles that have been modified (-r) or created (-p) since 90-days ago.
```bash
selitem -t"~PAPERBACK,JPAPERBACK,BKCLUBKIT,COMIC,DAISYRD,EQUIPMENT,E-RESOURCE,FLICKSTOGO,FLICKTUNE,JFLICKTUNE,JTUNESTOGO,PAMPHLET,RFIDSCANNR,TUNESTOGO,JFLICKTOGO,PROGRAMKIT,LAPTOP,BESTSELLER,JBESTSELLR" -l"~BARCGRAVE,CANC_ORDER,DISCARD,EPLACQ,EPLBINDERY,EPLCATALOG,EPLILL,INCOMPLETE,LONGOVRDUE,LOST,LOST-ASSUM,LOST-CLAIM,LOST-PAID,MISSING,NON-ORDER,BINDERY,CATALOGING,COMICBOOK,INTERNET,PAMPHLET,DAMAGE,UNKNOWN,REF-ORDER,BESTSELLER,JBESTSELLR,STOLEN" -oC 2>/dev/null | sort | uniq >catkeys.no_t.no_l.lst 
cat catkeys.no_t.no_l.lst | selcatalog -iC -p">`transdate -d-90`" -oC  >mixed.catkeys.90d.lst
cat catkeys.no_t.no_l.lst | selcatalog -iC -r">`transdate -d-90`" -oC  >>mixed.catkeys.90d.lst 
cat mixed.catkeys.90d.lst | sort | uniq >mixed.catkeys.90d.uniq.lst
cat mixed.catkeys.90d.uniq.lst | catalogdump -kf035 -of | grep -v -i -e '\.250\.[ \t]+\|aExpected release' >flat.wo.onorder.lst
cat flat.wo.onorder.lst | flatskip -if -aMARC -om >mixed.mrc
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[Apache2](https://choosealicense.com/licenses/apache-2.0/)



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