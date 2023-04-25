cat fullcat.csv | awk -F'""' '{print $1}' | awk -F'", "' '{print $2}' | awk -F'")' '{print $1}' > oclcnumbers.txt
