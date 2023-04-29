#!/usr/bin/env awk
# This script will parse any length of file containing flat catalog data
# and produce a list of 001, TCN and 035 fields as slim MARC 21 format.
# The script is intended to create slim marc files for merging with 
# existing marc records.
#
# Call the script on every flat record with 
# awk -v NEW_OCLC_NUMBER="(OCoLC)77778888" -f makeslimMARC.awk test.flat
# *** DOCUMENT BOUNDARY ***
# FORM=MUSIC               
# .035.   |a(OCoLC)77778888|z(OCoLC)987654321
# .035.   |a(Sirsi) 111111111

BEGIN {
    FS = "|";
}

/DOCUMENT BOUNDARY/ {
	# New record 
    print $0;
}

/^FORM=/ {
    print $0;
}

/\.035\./ {
	zeroThreeFive = substr($2, 2);
    if (zeroThreeFive ~ /\(OCoLC\)/) {
		# Make a new string that includes the 'z' sub-field of old data.
		printf ".035.   |a%s|z%s\n", NEW_OCLC_NUMBER, zeroThreeFive;
    } else {
        print $0;
    }
}
