#!/usr/bin/env awk
# This script will parse any length of file containing flat catalog data
# and produce a list of 001, TCN and 035 OCoLC numbers, in pipe-delimited format.
# The script also removes records with 250 that says 'Expected release' as
# EPL does not want those records going to OCLC. The result is a master list of 
# all the cat keys, 035 OCLC numbers and Flexkeys on one line as follows.
# cat_key | TCN  | OCLC_num

BEGIN {
 FS = "|"
 all035s = "";
 zeroZeroOne = "";
 zeroThreeFive = "";
 tcn = "";
}

/DOCUMENT BOUNDARY/ {
	if (zeroZeroOne != "") {
		gsub(/[ \t]+$/, "", zeroZeroOne)
		printf "%s|%s|%s\n", zeroZeroOne, tcn, all035s;
		all035s = "";
		tcn = "";
	}
}

/\.250\./ {
	# If the record contains the phrase 'Expected release' in the 250 field
	# don't output anything, these are not to be sent to OCLC.
	if ($2 ~ /Expected release/) {
		all035s = "";
		zeroZeroOne = "";
		zeroThreeFive = "";
		tcn = "";
	}
}

/\.035\./ {
	zeroThreeFive = substr($2, 2);
	# Capture the TCN for reference that the catalogers can use.
	if (zeroThreeFive ~ /\(Sirsi\) /) {
		# Remove the '(Sirsi) ' string from the front.
		gsub(/\(Sirsi\) /, "", zeroThreeFive)
		# Remove the trailing white space
		gsub(/[ \t]+$/, "", zeroThreeFive)
		if (tcn != "" && tcn != zeroThreeFive) {
			# If there was another Sirsi number issue warning if they are not the same as this _should_ never happen.
			printf "*TCN warning, replacing '%s' with '%s'\n", tcn, zeroThreeFive > "/dev/stderr";
		}
		tcn = zeroThreeFive;
	}
	if (zeroThreeFive ~ /\(OCoLC\)/) {
		# Remove the '(OCoLC)' string from the front.
		gsub(/\(OCoLC\)/, "", zeroThreeFive)
		# Remove the trailing white space
		gsub(/[ \t]+$/, "", zeroThreeFive)
		if (all035s != "" && all035s != zeroThreeFive) {
			# .035.   |a(OCoLC)809109558|z(OCoLC)835633369
			# later in record...
			# .035.   |a(OCoLC)809109558
			# If there was another OCoLC number issue warning as this _should_ never happen.
			printf "*OCLC warning, replacing '%s' with '%s'\n", all035s, zeroThreeFive > "/dev/stderr";
		} 
		all035s = zeroThreeFive;
	}
}

/\.001\./ {
	zeroZeroOne = substr($2, 2);
}

END {
	print "\n";
}
