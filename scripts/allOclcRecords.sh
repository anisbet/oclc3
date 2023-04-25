#!/bin/bash
##################################################################
# Generates all OCLC records from the catalog.
# Date: Feb. 15, 2023
# Copyright (C) Andrew Nisbet 2023
##################################################################
. ~/.bashrc
# Logs messages to STDOUT and $LOG_FILE file.
# param:  Message to put in the file.
# param:  (Optional) name of a operation that called this function.
logit()
{
    local message="$1"
    local time=$(date +"%Y-%m-%d %H:%M:%S")
    if [ -t 0 ]; then
        # If run from an interactive shell message STDOUT and LOG_FILE.
        echo -e "[$time] $message" | tee -a $LOG_FILE
    else
        # If run from cron do write to log.
        echo -e "[$time] $message" >>$LOG_FILE
    fi
}
ILS='edpl.sirsidynix.net'
HOST=`hostname`
[ "$HOST" -ne "$ILS" ] && { logit "*error, script must be run on a Symphony ILS."; exit 1; }
VERSION="2.06.04"
BIN_PATH=~/Unicorn/Bin
SELITEM=$BIN_PATH/selitem
CATALOG_DUMP=$BIN_PATH/catalogdump
NOWRAP=~/Unicorn/Bincustom/nowrap.pl
[ -f "$SELITEM" ] || { logit "*error, missing $SELITEM."; exit 1; }
[ -f "$CATALOG_DUMP" ] || { logit "*error, missing $CATALOG_DUMP."; exit 1; }
[ -f "$NOWRAP" ] || { logit "*error, missing $NOWRAP."; exit 1; }
LOG_FILE="allOclcRecords.log"
logit "Starting item selection"
selitem -t"~PAPERBACK,JPAPERBACK,BKCLUBKIT,COMIC,DAISYRD,EQUIPMENT,E-RESOURCE,FLICKSTOGO,FLICKTUNE,JFLICKTUNE,JTUNESTOGO,PAMPHLET,RFIDSCANNR,TUNESTOGO,JFLICKTOGO,PROGRAMKIT,LAPTOP,BESTSELLER,JBESTSELLR" -l"~BARCGRAVE,CANC_ORDER,DISCARD,EPLACQ,EPLBINDERY,EPLCATALOG,EPLILL,INCOMPLETE,LONGOVRDUE,LOST,LOST-ASSUM,LOST-CLAIM,LOST-PAID,MISSING,NON-ORDER,BINDERY,CATALOGING,COMICBOOK,INTERNET,PAMPHLET,DAMAGE,UNKNOWN,REF-ORDER,BESTSELLER,JBESTSELLR,STOLEN" -oC 2>/dev/null | 
 sort | uniq >/tmp/catkeys.wo_types.wo_locations.lst 
logit "Creating flat files without on-order titles"
cat /tmp/catkeys.wo_types.wo_locations.lst | 
catalogdump -kf035 -of 2>/dev/null | 
nowrap.pl | 
grep -v -i -e '\.250\.[ \t]+\|aExpected release' >all_records.flat
# We'll use the flat file later to make any XML required to add records if needed.
logit "Distilling list of OCLC numbers"
awk -F"|a" '{ if ($2 ~ /\(OCoLC\)/) { oclcnum = $2; gsub(/\(OCoLC\)/, "", oclcnum); print oclcnum; }}' all_records.flat >librarynumbers.txt
logit "All the records can be found in 'all_records.flat' and the OCLC numbers in 'librarynumbers.txt'"
logit "compressing files into 'oclc.zip'"
zip oclc.zip all_records.flat librarynumbers.txt
logit "done"
