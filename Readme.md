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

##
This tool outputs catalog information about items, as an example:
```bash
head mixed.catkeys.90d.lst | xmlitem -iC -cf -e035,008,250 # Other tags can be added.
```
```xml
<?xml version="1.0" encoding="UTF-8"?>
<titles><record>
<catalog>
<marc primary_key="0|18557578|">
<marc_field tag="035" label="DBCN">LSC2167473</marc_field><marc_field tag="008" label="Fixed field data">090818t20112009nyua   e b    001 0beng d</marc_field></marc>
</catalog>
</record>
<record>
<catalog>
<marc primary_key="0|18579075|">
<marc_field tag="035" label="DBCN">LSC3020594</marc_field><marc_field tag="008" label="Fixed field data">160408s2016    onc    e b    000 0 eng</marc_field><marc_field tag="250" label="Edition">First edition.</marc_field></marc>
</catalog>
</record>
<record>
<catalog>
<marc primary_key="0|18578920|">
<marc_field tag="035" label="DBCN">LSC3072940</marc_field><marc_field tag="008" label="Fixed field data">171020s2017    nyuab  e b    001 0 eng d</marc_field></marc>
</catalog>
</record>
<record>
<catalog>
<marc primary_key="0|18153232|">
<marc_field tag="035" label="DBCN">LSC3124188</marc_field><marc_field tag="008" label="Fixed field data">221107s2022    xxc    e      001 0 eng</marc_field><marc_field tag="250" label="Edition">ON ORDER</marc_field></marc>
</catalog>
</record>
<record>
<catalog>
<marc primary_key="0|18563765|">
<marc_field tag="035" label="DBCN">LSC3586037</marc_field><marc_field tag="008" label="Fixed field data">180907s2019    cau    e      000 0 eng</marc_field></marc>
</catalog>
</record>
<record>
<catalog>
<marc primary_key="0|18153234|">
<marc_field tag="035" label="DBCN">LSC3673686</marc_field><marc_field tag="008" label="Fixed field data">221107s2022    xxc    e      001 0 eng</marc_field><marc_field tag="250" label="Edition">ON ORDER</marc_field></marc>
</catalog>
</record>
<record>
<catalog>
<marc primary_key="0|18641535|">
<marc_field tag="035" label="DBCN">LSC3679913</marc_field><marc_field tag="008" label="Fixed field data">190425s2020    caua   e b    001 0 eng</marc_field></marc>
</catalog>
</record>
<record>
<catalog>
<marc primary_key="0|18153236|">
<marc_field tag="035" label="DBCN">LSC3741897</marc_field><marc_field tag="008" label="Fixed field data">221107s2022    xxc    e      001 0 eng</marc_field><marc_field tag="250" label="Edition">ON ORDER</marc_field></marc>
</catalog>
</record>
<record>
<catalog>
<marc primary_key="0|18153237|">
<marc_field tag="035" label="DBCN">LSC3853355</marc_field><marc_field tag="008" label="Fixed field data">221107s2022    xxu    e      001 0 eng</marc_field><marc_field tag="250" label="Edition">ON ORDER</marc_field></marc>
</catalog>
</record>
<record>
<catalog>
<marc primary_key="0|18153238|">
<marc_field tag="035" label="DBCN">LSC3875635</marc_field><marc_field tag="008" label="Fixed field data">221107s2022    xxc    e      001 0 eng</marc_field><marc_field tag="250" label="Edition">ON ORDER</marc_field></marc>
</catalog>
</record>
</titles>
```

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