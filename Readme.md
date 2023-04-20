# OCLC Holdings Management

`oclc` is a Python application to manage library holdings in OCLC's [WorldCat discovery](https://www.worldcat.org/) database through [WorldCat Metadata web services](https://www.oclc.org/developer/develop/web-services.en.html). [See here for more information](#regular-worldcat-maintenance).

## Requesting Web Services Keys
you can get info about keys [from this link](https://www.oclc.org/developer/api/keys.en.html) and [request keys here](https://authn.sd00.worldcat.org/wayf/metaauth-ui/cmnd/protocol/samlpost) after entering your institution's symbol.

# Spec for Reporting
* Report how long the script ran.
* Report total hits and breakdown by operation.
* Checks should report the original sent and value returned by OCLC and if an update is required. Updating this information could be in a report that could be made available to CMA for record updating, but automating is out of scope for now.
* Adds and delete counts shall be reported along with any errors.
* The master list (receipt) shall be updated with what happened with either of the following.
  * ` - success` if everything went as planned.
  * ` - error [reason]`, on error output the error.
  * ` - pending` if the web service hit count exceeded quota
  * ` - updated [new]` if the two numbers differ, and ` - success` if no change required.

## Testing
The application is controlled by a YAML file which contains the following values.
```yaml
# Setting oclc3 uses, 
service: 
  name:          'WCMetaDataTest'
  clientId:      'some_long_hex_string'
  secret:        'p@ssW0rD!_or_something stronger'
  registryId:    '128807' # Test registry ID supplied by OCLC.
  principalId:   'a_long_hash_string_identifier' # Provided but not used.
  principalIdns: 'urn:oclc:wms:da' # Provided but not used.
  institutionalSymbol: 'OCPSB' # Test institutional symbol supplied by OCLC.
report: 'oclc.log'

# Configurations for the database.
database:
  name: 'oclc.db'
  path: '..'   # Location of the database file relative to the 'lib/' directory.
  add_table_name: 'added' # Table name
  del_table_name: 'deleted' # Table name - can be (almost) anything you like.
```
Once set up the script can be run from the command line as follows.
### Help
```bash
# For help use...
python3 oclc.py --help
usage: oclc [options]

Maintains holdings in OCLC WorldCat Search.

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -c [/foo/check.lst], --check [/foo/check.lst]
                        Check if the OCLC numbers in the list are valid.
  -d, --debug           turn on debugging.
  -l [/foo/local.lst], --local [/foo/local.lst]
                        Local OCLC numbers list collected from the library's ILS.
  -r [/foo/remote.lst], --remote [/foo/remote.lst]
                        Remote (OCLC) numbers list from WorldCat holdings report.
  -s [/foo/bar.txt], --set [/foo/bar.txt]
                        OCLC numbers to add or set in WorldCat.
  -u [/foo/bar.txt], --unset [/foo/bar.txt]
                        OCLC numbers to delete from WorldCat.
  --update_instructions UPDATE_INSTRUCTIONS
                        File that contains instructions to update WorldCat. Default master.lst
  -x XML_RECORDS, --xml_records XML_RECORDS
                        file of MARC21 XML catalog records to submit as special local holdings.
  -y [/foo/test.yaml], --yaml [/foo/test.yaml]
                        alternate YAML file for testing.

See "-h" for help more information.
```
### Add / Set OCLC numbers
See [the add documentation](#regular-worldcat-maintenance) for more information.
```bash
# With a list of OCLC numbers to add/update on OCLC's sandbox with
# a file of OCLC numbers called add_me.lst...
python3 oclc.py --yaml=test.yaml --set add_me.lst
 ...
```

### Delete / Unset OCLC numbers
See [the delete documentation](#delete--unset-oclc-numbers) for more information.
```bash
# Delete or unset the OCLC numbers in 'delete_me.lst' using OCLC's 
# production database...
python3 oclc.py --yaml=production.yaml --unset delete_me.lst
 ...
```

### Reclamation
See [this section on reclamation](#reclamations-instructions) for more information.
```bash
# Perform reclamation-like operation on OCLC's production database. 
python3 oclc.py --yaml=production.yaml --remote oclc_reported_holdings.lst --local our_current_holdings.lst
 ...
```


## Installation

* Clone the project from [GitHub](https://github.com/anisbet/oclc3) a clean folder.
* Get API keys from [here](https://authn.sd00.worldcat.org/wayf/metaauth-ui/cmnd/protocol/samlpost).
* Create a YAML file of you site's [OCLC settngs](#required-oclc-settings).
* Make sure python 3.7 (minimum) is installed and install libraries in a virtual environment (`venv`).
  * Create a virtual environment (`venv`) with `python3 -m venv oclcvenv`
  * Use the `venv` with `. oclcvenv/bin/activate`
  * Update `pip` with `pip install --upgrade pip`
  * Install wheel with `pip install wheel`
  * Install helper libraries. To date: `pip install pyyaml requests`. There may be others listed in the `requirements.txt` file, but requests and pyyaml install dependancies with those and run the next step. Any errors will alert you to any other missing libraries. 
  * Test by setting the `TEST` variable in `oclc.py` to `True` and running `python oclc.py`
  * Set `TEST` to `False`
* Run as described in either the [maintenance](#regular-worldcat-maintenance) or [reclamation](#reclamations-instructions) sections.
* Schedule and test.

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

## Notes on OCLC Number Lists
The specification for a valid list of OCLC numbers is as follows.
* An OCLC number is a string of 4 or more digits that together satisfy the definition of an integer, that is, no float values.
* A valid file contains one or more OCLC numbers, one per line.
* A valid OCLC number is an integer of 4 or more digits and may start with a `+`, `?`, or `-`.
* Any number prefixed with `+`, like `+9974113 *`, or `+(OCoLC)9974113 *` indicates the record should be added or set as a holding. If you are using `--unset` this number will be ignored.
* Any line that starts with `-`, like `-2239776 *` or `-(OCoLC)12345` means delete this record when the `--unset` switch is used, otherwise this line is ignored.
* Any line that start with a space ` `, like ` 225716 *`, or ` (OCoLC)123456` will be ignored when using `--set` or `--unset`.
* A `master.lst` file is written to the local directory which contains the instructions that were executed for each OCLC number of either `--set`, `--unset`, `--local`, or `--remote`.

While this sounds complicated, there are some simple rules.
1) If you use a file to **set** records only lines that start with `\d{4,}` or `+\d{4,}` will be added.
2) If you `--unset` any line that starts with `\d{4,}` or `-\d{4,}` will be deleted. Any other lines will be ignored.
3) The flags `--local` and `--remote` must be used together.
4) You can use the same `master.lst` with both `--set` or `--unset` switches.

## Example of a Number List
```bash
+123456 Treasure Isl... # The record 123456 will be added when '--set' is used.
123456 Treasure Isla... # Added when using '--set' and deleted if using `--unset`.
-7756632                # Delete this record if '--unset' is used.
7756632                 # Deleted if '--unset' is used, added if using '--set' or `--local`.
 654321 any text        # This will be ignored in all cases.
(OCoLC)7756632  blah    # Set or unset the number '7756632' depending on flag.
-(OCoLC)7756632  blah   # Unset number '7756632' if '--unset' is used, ignored otherwise.
(OCoLC)7756632  blah    # Set or unset the number '7756632' depending on switch.
?(OCoLC)7756632  blah   # Check number '7756632'.
Random text on a line   # Ignored.
```

## OCLC3 Reclamation

1) On the ILS, select all the records that OCLC should be aware of. [A suggestion of Symphony API instructions can be found here.](#library-records). This will become the **local** list.
2) Generate a report of all the records OCLC has for your institution. [See here for hints on how to generate a report of your holdings.](#oclc-records). This will become the **remote** list.
3) Use the command `python3 oclc.py --local=local.lst --remote=remote.lst`. This will generate a master list of record instructions with [patch notation]().

## OCLC Records
1) Create a report of all the titles from the library by logging into OCLC's [WorldShare Administration Portal](https://edmontonpl.share.worldcat.org/wms/cmnd/analytics/myLibrary).
2) Once logged in select the ```Analytics``` tab.
3) Select Collection Evaluation and click the ```My Library``` button.
4) Below the summary table select export title list, and dismiss the dialog telling you how long it will take. Expect at least **1.5+ hours**.
5) Download the zipped XSL file from the ```My Files``` menu on the left of the page, and unzip.
6) You can use ```pandas``` or ```excel``` to open and analyse, but I have more luck with `OpenOffice`.
**Hint**:
   1) Open the ```xls``` in ```OpenOffice``` sheets as a **fixed width** document.
   2) Save as `csv` to file ```full_cat.csv```.
   3) Use awk to process: ```cat full_cat.csv | awk -F'""' '{print $1}' | awk -F'", "' '{print $2}' | awk -F'")' '{print $1}' > oclcnumbers.txt``` to capture all the OCLC numbers.
      1) **Explanation**: awk 1 splits the file on double-double-quotes, and outputs the first field which is a `HYPERLINK`.
      2) Awk 2 takes the `HYPERLINK` data and further splits that on the only remaining quotes of the `url` and oclc number. It outputs a line that starts with a the oclc number and ends in `")`.
      3) Awk 3 further splits on the afore-mentioned `")`, and outputs field 1.
   4) To check ```wc -l full_cat.csv``` compared with ```wc -l oclcnumbers.txt```.
   5) To check that all the lines have values use ```cat oclcnumbers.txt | pipe.pl -zc0 | wc -l```. It should show the same number of lines as the `csv`.
7) Select all the OCLC numbers from your library's catalog with API. Typically selection is restricted to titles that you want to appear in WorldCat searches; not electronic resources, internet databases, or non-circulating items. See [this section](#library-records) for example instructions for a SirsiDynix Symphony ILS.
8) Use `oclc.py` to create a master list by using `--remote=oclcnumbers.txt` and `--local=librarynumbers.txt`. This will create a master list (`master.lst`) in the current directory. Examine the results and see the delta of OCLC and your library. 
   1) Records that OCLC are missing are marked with `+`.
   2) Records that OCLC has but your library no longer has are marked with `-`.
   3) Records that don't need attention start with a space (` `).
9) **TODO: confirm!** Use the `master.lst` with the `--update` flag and `oclc.py` will use these instructions to operate the OCLC web service. The order of operations are as follows.
   1)  Checks
   2)  Deletes
   3)  Adds

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