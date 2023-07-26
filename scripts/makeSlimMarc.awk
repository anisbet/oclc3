#!/usr/bin/env awk
#
# This script create a slim flat file in preparation for use with catalogmerge. 
# The script places a 'NEW_OCLC_NUMBER' sentinel in the record where the 
# the number needs to be filled in by another process.
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
# awk -f makeslimMarc.awk test.flat
#
# *** DOCUMENT BOUNDARY ***
# FORM=MUSIC               
# .001. |aon1347755731     
# .035.   |aNEW_OCLC_NUMBER|z(OCoLC)987654321
# .035.   |a(Sirsi) 111111111
# .035.   |aNEW_OCLC_NUMBER|z(OCoLC)77777777

BEGIN {
    FS = "|";
}

# New bib record 
/DOCUMENT BOUNDARY/ {
    print $0;
}

# Bib format
/^FORM=/ {
    print $0;
}

# Use the 001 (TCN / Flexkey) as match point when merging records.
/\.001\./ {
    print $0;
}

/\.035\./ {
	myZeroThreeFiveValue = substr($2, 2);
    if (myZeroThreeFiveValue ~ /\(OCoLC\)/) {
		# Make a new string that includes the 'z' sub-field of the old data.
		printf ".035.   |a%s|z%s\n", "NEW_OCLC_NUMBER", myZeroThreeFiveValue;
    } else {
        print $0;
    }
} 
