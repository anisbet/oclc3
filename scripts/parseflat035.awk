#!/usr/bin/env awk
# This script will parse any length of file containing flat catalog data
# and produce a list of 001 and 035 OCoLC numbers, in pipe-delimited format.
# The script also removes records with 250 that says 'Expected release' as
# EPL does not want those records going to OCLC.
BEGIN {
 FS = "|"
 all035s = "";
 zeroZeroOne = "";
 zeroThreeFive = "";
}

/DOCUMENT BOUNDARY/ {
	if (zeroZeroOne != "") {
		gsub(/[ \t]+$/, "", zeroZeroOne)
		printf "%s|%s\n", zeroZeroOne, all035s;
		all035s = "";
	}
}

/\.250\./ {
	# If the record contains the phrase 'Expected release' in the 250 field
	# don't output anything, these are not to be sent to OCLC.
	if ($2 ~ /Expected release/) {
		all035s = "";
		zeroZeroOne = "";
		zeroThreeFive = "";
	}
}

/\.035\./ {
	zeroThreeFive = substr($2, 2);
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
			printf "*warning, replacing '%s' with '%s'\n", all035s, zeroThreeFive > "/dev/stderr";
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
