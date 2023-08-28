# OCLC Holdings Management

`oclc.py` is a Python application that synchronizes your library's holdings with OCLC's [WorldCat](https://www.oclc.org/en/worldcat.html) discovery service.

There are two ways to maintain holdings at OCLC, [batch process](#batch-process) and [web services](#worldcat-metadata-web-service).

Edmonton Public Library (EPL) has decided to move from an automated batch process to the web service. Web services are faster, and offer feedback useful for synchronizing titles between the local library and OCLC.

Here are some strategies a library can use to maintain holdings.
1) Wipe the slate clean. The library removes all its records from OCLC and repopulates them with their current titles. OCLC refers to this as [reclamation](#oclc3-reclamation).
2) Incremental updates. The library opts to send periodic updates of catalog additions and deletions.
3) A combo of 1 and 2. The library sends weekly updates, and annually performs a reclamation. I would recommend this option and time frame for a large library.

This appliction can do much of the heavy lifting for any of these strategies. It is designed to be [automated](#automation), but has some [limitations](#limitations) based on the current level of development.


# Automation
The application can perform the following operations unattended.
1) Read catalog records in SirsiDynix's flat format, which then can be used with or instead of a `--local` file.
2) Read the OCLC report if it is [converted from XSLX to CSV](#hints-for-oclc-report-of-holdings).

# Limitations
Currently `oclc.py` has the following limitations.
1) OCLC report generation. It should be feasible to set up, run, and collect the OCLC report of holdings, but that work is out of scope for now. The report must be generated through the portal, downloaded, and converted to CSV.
2) The remote lists may be CSV or a standard list of OCLC numbers. [There is some flexibility in parsing lists](#example-of-a-number-list).
3) Updating local records between OCLC and the library. Many records supplied by vendors don't include OCLC numbers. Those records need to be converted into OCLC XML and submitted. **It isn't known at this time if the response includes a useful number that can be added to the local record so it can be maintained.**


## Hints for OCLC Report of Holdings
1) Open the `xsls` in `OpenOffice` sheets and in the `Text Import` modal dialog box click the `Fixed Width` radio button, and from the `Other Options` section select the `Format quoted fields as text` checkbox.
2) Save as `csv` to file .
3) Use `oclc.py`'s --csv switch to read the report. It will be used with or in lieu of a `--remote` list.
### Batch Process
Previously our library used a batch process. A script ran weekly and collected all the added and modified records from the previous week, formatted them into MARC, and uploaded them to an SFTP site. One challenge of this process is identifying what records have been deleted since they are no longer in the catalog. An additional challenge is that OCLC regularly updates their catalog numbers, and there was no way to feedback this information to the ILS.

### WorldCat Metadata Web Service
A better way to synchronize OCLC holdings is by the [WorldCat MetaData API](https://developer.api.oclc.org/wc-metadata-v2?_gl=1*dpl1t0*_gcl_au*MTg2OTUyMTM2LjE2OTAzMTQzODg.). By adding (`set`ting) and deleting (`unset`ting) your OCLC numbers your titles will appropriately show or not show up in customer searches in [WorldCat](https://www.oclc.org/en/worldcat.html). 

The basic steps are [Generate a CSV report](#reclamations-instructions) of your OCLC holdings from the self-service portal. This will be the _remote_ list. [Create a  list of your library's collection](#library-records) called the _local_ list. Use `oclc.py` to analyse both lists and produce a report which serves as both documentation and instructions on how to synchronize OCLC holdings to your collection.  

[To get started you will need API keys](#requesting-web-services-keys).

# Requesting Web Services Keys
To use the OCLC WorldCat Metadata API you will need authentication keys. Members with an institution symbol [can apply for keys here](https://authn.sd00.worldcat.org/wayf/metaauth-ui/cmnd/protocol/samlpost) and can [find more information about keys here](https://www.oclc.org/developer/api/keys.en.html).

## Logs
* Report how long the script ran.
* Report total hits and breakdown by operation.
* Checks should report the original sent and value returned by OCLC and if an update is required. Updating this information could be in a report that could be made available to CMA for record updating, but automating is out of scope for now.
* Adds and delete counts shall be reported along with any errors.
* The master list (receipt) shall be updated with what happened with either of the following.
  * ` - success` if everything went as planned.
  * ` - error [reason]`, on error output the error.
  * ` - pending` if the web service hit count exceeded [quota](#web-service-quotas). See also [this section](#yaml-configuration) for examples of how to set quotas.
  * ` - updated [new]` if the two numbers differ, and ` - success` if no change required.

## Yaml Configuration
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
ignoreTags: 
  '250': 'Expected release'
hitsQuota:       100
dataDir:         'data'
```
Once set up the script can be run from the command line as follows.
## Help
```bash

```
### Add / Set OCLC numbers
See [the add documentation](#regular-worldcat-maintenance) for more information.
```bash
# With a list of OCLC numbers to add/update on OCLC's sandbox with
# a file of OCLC numbers called add_me.lst...
python oclc.py --yaml=test.yaml --set add_me.lst
 ...
```

### Delete / Unset OCLC numbers
See [the delete documentation](#delete--unset-oclc-numbers) for more information.
```bash
# Delete or unset the OCLC numbers in 'delete_me.lst' using OCLC's 
# production database...
python oclc.py --yaml=production.yaml --unset delete_me.lst
 ...
```

### Reclamation
See [this section on reclamation](#reclamations-instructions) for more information.
```bash
# Perform reclamation-like operation on OCLC's production database. 
python oclc.py --yaml=production.yaml --remote oclc_reported_holdings.lst --local our_current_holdings.lst
python oclc.py --update_instructions=master.lst --update --yaml=production.yaml 
 ...
```


## Installation

* Clone the project from [GitHub](https://github.com/anisbet/oclc3) a clean folder.
* Get API keys from [here](https://authn.sd00.worldcat.org/wayf/metaauth-ui/cmnd/protocol/samlpost).
* Create a YAML file of you site's [OCLC settngs](#required-oclc-settings).
* Make sure python 3.7 (minimum) is installed and install libraries in a virtual environment (`venv`).
  * Create a virtual environment (`venv`) with `python -m venv oclcvenv`
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

The **oclc.py** script allows for the maintenance of holdings at OCLC by supporting each of these functions.
1) Setting holdings - which, when using the old batch process, where known as *updates* and *creates*.
2) Unsetting holdings - Also known as *deletes* in batch processing.
3) Local Holdings Submission - Previously this was simply covered by the *creates* and *updates* in the batch process.

# Reclamations Instructions
As mentioned before, records were maintained at OCLC through a batch process which consisted of collecting all new and updated records of interest and submitting slim MARC records to OCLC. Deletes were handled by searching the ILS logs for remove title commands which is the only surviving evidence of a purged title in the ILS. Typically the search starts from the last time the batch ran, remove title commands may be missed if they occurred outside of the search time-frame window. 

The result is sometimes titles didn't get unset, and customers would get upset that the library indicates they have the title but they don't. 

To fix the mismatch of library's holdings OCLC offers a **reclamation** service. At the library's request and a cost of a few thousands of dollars, OCLC will purge all the holdings for a library and the library submits a complete new set.

To remediate this expense and improve customer service `oclc.py` can run a reclamation process.

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

## Web Service Quotas
Each of the operations of `check`, `add`, and `delete` can have applied quotas which prevents the application exceeding OCLC's web service API call quotas. Quotas are optional and if missing from the yaml file, `oclc.py` will attempt to complete all the instructions on the `master.lst`.

With a quota set, once the limit is reached the `master.lst` is updated with the remaining instructions to do when the script is restarted.

## Example of a Number List
**NOTE: While this technique is supported, `oclc.py` can now read and update `flat` files. It is therefore the preferred method of creating a submission.**

The following illustrates the types of strings that `oclc.py` can read and how they will be interpreted.


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
3) Use the command `python oclc.py --local=local.lst --remote=remote.lst`. This will generate a master list of record instructions with [patch notation]().

## OCLC Records
1) Create a report of all the titles from the library by logging into OCLC's [WorldShare Administration Portal](https://edmontonpl.share.worldcat.org/wms/cmnd/analytics/myLibrary). For EPL the URL is [https://edmontonpl.share.worldcat.org/wms/cmnd/analytics/myLibrary](https://edmontonpl.share.worldcat.org/wms/cmnd/analytics/myLibrary) but your library will have it's own portal.
2) Once logged in select the `Analytics` tab and make sure you are on the page with the `My Library` heading. If not select `Collection Evaluation` and then the `My Library` button.
3) Below the summary table select `Export Title List` button, give the report a name and description if desired, and dismiss the dialog box telling you how long it will take. Expect at least **1.5+ hours**.
4) After the appropriate time has elapsed, re-login to the [portal](https://edmontonpl.share.worldcat.org/wms/cmnd/analytics/myLibrary) and navigate to the `Analytics` tab. Select the `My Files` menu on the left margin of the page, click the `Download Files` button. Download, and unzip the compressed XSL report.
5) You can use `excel` to open and save as CSV, but I use `OpenOffice`.

6) Select all the OCLC numbers from your library's catalog with API. Typically selection is restricted to titles that you want to appear in WorldCat searches; not electronic resources, internet databases, or non-circulating items. See [this section](#library-records) for example instructions for a SirsiDynix Symphony ILS.
7) Use `oclc.py` to create a master list by using `--remote=oclcnumbers.txt` and `--local=librarynumbers.txt`. Optionally use the `--flat` switch to use the OCLC numbers from a flat file directly. Any numbers found in the flat file will be appended to the `--local` list if provided. This will create a master list (`master.lst`) in the current directory. Examine the results and see the delta of OCLC and your library. 
   1) Records that OCLC are missing are marked with `+`.
   2) Records that OCLC has but your library no longer has are marked with `-`.
   3) Records that don't need attention start with a space (` `).
   4) Lines that start with `?` indicate that the OCLC number should be confirmed.
8) Use the `--update_instructions=master.lst` as the instruction file and `--update` flag to actually do the work. The order of operations are as follows.
   1)  Checks
   2)  Deletes
   3)  Adds

## Library Records
The Sympony API to collect data for submission to OCLC is listed below.
```bash
selitem \ 
-t"~PAPERBACK,JPAPERBACK,BKCLUBKIT,COMIC,DAISYRD,EQUIPMENT,E-RESOURCE,FLICKSTOGO,FLICKTUNE,JFLICKTUNE,JTUNESTOGO,PAMPHLET,RFIDSCANNR,TUNESTOGO,JFLICKTOGO,PROGRAMKIT,LAPTOP,BESTSELLER,JBESTSELLR" \ 
-l"~BARCGRAVE,CANC_ORDER,DISCARD,EPLACQ,EPLBINDERY,EPLCATALOG,EPLILL,INCOMPLETE,LONGOVRDUE,LOST,LOST-ASSUM,LOST-CLAIM,LOST-PAID,MISSING,NON-ORDER,BINDERY,CATALOGING,COMICBOOK,INTERNET,PAMPHLET,DAMAGE,UNKNOWN,REF-ORDER,BESTSELLER,JBESTSELLR,STOLEN" \ 
-oC 2>/dev/null | sort | uniq >oclc_catkeys.lst 
cat oclc_catkeys.lst | catalogdump -oF -kf >all_records.flat
# The oclc.py can read flat files.
```

Once done use `oclc.py` script's `--local` can be used to create a master list of OCLC numbers. Those marked with `+` need to be set, those with `-` need to be unset, `?` means check the number, and a ` ` indicates nothing needs to be done.

## Complete Mixed selection shell commands
**TODO Check this over. The code below only removes the 250 tags not the on order records themselves.**
That is titles that have been modified (-r) or created (-p) since 90-days ago.
```bash
selitem -t"~PAPERBACK,JPAPERBACK,BKCLUBKIT,COMIC,DAISYRD,EQUIPMENT,E-RESOURCE,FLICKSTOGO,FLICKTUNE,JFLICKTUNE,JTUNESTOGO,PAMPHLET,RFIDSCANNR,TUNESTOGO,JFLICKTOGO,PROGRAMKIT,LAPTOP,BESTSELLER,JBESTSELLR" -l"~BARCGRAVE,CANC_ORDER,DISCARD,EPLACQ,EPLBINDERY,EPLCATALOG,EPLILL,INCOMPLETE,LONGOVRDUE,LOST,LOST-ASSUM,LOST-CLAIM,LOST-PAID,MISSING,NON-ORDER,BINDERY,CATALOGING,COMICBOOK,INTERNET,PAMPHLET,DAMAGE,UNKNOWN,REF-ORDER,BESTSELLER,JBESTSELLR,STOLEN" -oC 2>/dev/null | sort | uniq >oclc_ckeys.lst 
cat oclc_ckeys.lst | selcatalog -iC -p">`transdate -d-90`" -oC  >oclc_catalog_selection.lst
cat oclc_ckeys.lst | selcatalog -iC -r">`transdate -d-90`" -oC  >>oclc_catalog_selection.lst 
cat oclc_catalog_selection.lst | sort | uniq >oclc_catalog_selection.uniq.lst
# Output the flat records as a flat file.
# If the records don't wrap, pipe it to flatskip -if -aMARC -om >mixed.flat
# -oF outputs the flat record without linewrapping.
# -kf outputs the flexkey TCN in the 001 for matching.
cat oclc_catalog_selection.uniq.lst | catalogdump -oF -kf >oclc_submission.flat
```
# Updating the Library's Catalog Records
The `oclc.py` will use information in oclc's responses to create a slim-flat file for overlaying updated OCoLC numbers in the `035` tag. The slim-flat file can then be used with Symphony's `catalogmerge` API command to update the ILS.

**Note:** `catalogmerge` can either delete all the `035` tags or add the new one(s) to the record. I have opted to use the delete option to avoid duplicates. This requires preserving all non-OCLC `035` tags and replacing the OCLC tags with updated values. See below.

```bash
*** DOCUMENT BOUNDARY ***
FORM=MUSIC                      
.001. |aon1347755731     
.035.   |a(OCoLC)1000001234|z(OCoLC)987654321
.035.   |a(Sirsi) on1347755731
.035.   |a(EPL) on1347755731
  ...
```

**TODO Finish this documentation after design is complete.**

Once done we can use `catalogmerge` to update the bib record with the data from the slim file with the following.

```bash
# -if flat ascii records will be read from standard input.
# -aMARC (required) specifies the format of the record.
# -b is followed by one option to indicate how bib records will be matched
#       for update.
#     c matches on the internal catalog key.
#     f(default) matches on the flexible key.
#     n matches on the call number key.
# -d delete all existing occurrences of entries being merged.
# -f is followed by a list of options specifying how to use the flexible key.
#    g use the local number as is (001). *TCN*
# -r reorder record according to format. Don't reorder. It messes with diffing results.
# -l Use the format to determine the tags to be merged. If the tag is
#      marked as non-repeatable, do not merge if the Symphony record contains
#      the tag. If the tag is non-repeatable, and the Symphony record does not
#      contain the tag, merge the tag into Symphony. If the tag is marked as
#      repeatable, the tag will be merged. This option is not valid if
#      the '-t' is used. If this '-t' is not used, this option is required.
#  == or ==
# -t list of entry id's to merge. This option is not valid if the '-l' is
#      used. If the '-l' is not specified, the '-t' is required.

cat oclc_updated.flat | catalogmerge -if -aMARC -bf -fg -d -r -t035  oclc_update_20230726.err >oclc_update_20230726.lst
```
Alternatively the `catalogmerge` command can take `-l` as described above, but then the `-t` can't be used. If you don't use `-t` you must use `-d`.

```bash
# Try this but the previous will probably work better.
cat oclc_updated.flat | catalogmerge -if -aMARC -bf -fg -d -r -l oclc_update_20230726.err >oclc_update_20230726.lst
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

## Symphony XML Item Tool
This tool outputs catalog information about items, as an example:
```bash
head oclc_catalog_selection.lst | xmlitem -iC -cf -e035,008,250 # Other tags can be added.
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