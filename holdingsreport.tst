>>> from holdingsreport import HoldingsReport 
>>> hr = HoldingsReport("test_data/testreport.csv", debug=True)
DEBUG: reading test_data/testreport.csv
0 => 267
1 => 1210
2 => 1834
3 => 2032
4 => 2290
read 20 records.
['267', '1210', '1834', '2032', '2290', '2340', '2579', '3051', '5065', '8045', '1382430182', '1382679733', '1382830360', '1382830375', '1382830392', '1385166509', '1389537317', '1389537359', '1390632770', '1390633246']


Test that a file is written.
>>> hr.write_list()
wrote 20 records to test_data/testreport.lst.
