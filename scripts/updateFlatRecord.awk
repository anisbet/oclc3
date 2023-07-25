#!/usr/bin/env awk
#
# This script will update all 035 tags that include OCLC data. 
# Because 035 tags are repeatable and sometimes a record can contain
# multiple 035 tags with conflicting OCLC numbers, each one of them
# is modified to have the new number and a subfield 'z' of the old
# numbers. All additional non-035 tags are output unmolested.
#
# Example of calling the script on the command line is as follows. Given
# the following arbitrary but specific FLAT MARC record file:
#
# *** DOCUMENT BOUNDARY ***
# FORM=MUSIC               
# .000. |ajm7i0n a         
# .001. |aon1347755731     
# .596.   |a1
# .035.   |a(OCoLC)987654321
# .035.   |a(Sirsi) 111111111
# .035.   |a(OCoLC)77777777
# 
# Given that a web response log produced by oclc3.py, OCLC reports the following:
# +1002126265  updated to 970392037, Record not found for holdings operation
# +1005006688  added
# + ... 
#
# From the first line of the report:
#
# '+1002126265  updated to 970392037, Record not found for holdings operation'
#
# we know that the new number is '970392037', and replaces the number 
# from the catalog '1002126265'.
#
# awk -v NEW_OCLC_NUMBER="(OCoLC)970392037" -f makeslimMARC.awk test.flat
#
# *** DOCUMENT BOUNDARY ***
# FORM=MUSIC               
# .000. |ajm7i0n a         
# .001. |aon1347755731     
# .596.   |a1
# .035.   |a(OCoLC)970392037|z(OCoLC)987654321
# .035.   |a(Sirsi) 111111111
# .035.   |a(OCoLC)970392037|z(OCoLC)77777777

BEGIN {
    FS = "|";
}

/\.035\./ {
	myZeroThreeFiveValue = substr($2, 2);
    if (myZeroThreeFiveValue ~ /\(OCoLC\)/) {
		# Make a new string that includes the 'z' sub-field of the old data.
		printf ".035.   |a%s|z%s\n", NEW_OCLC_NUMBER, myZeroThreeFiveValue;
    } else {
        print $0;
    }
    next;
} 

{
    # Print all other tags unmolested. I'm not sure what are the minimum
    # tags required to overlay MARC data in Symphony, so I have opted to
    # output all the tags provided and only modify the 035s with (OCoLC).
    print;
}