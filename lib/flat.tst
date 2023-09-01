>>> from flat import Flat 
>>> flat = Flat("../test_data/test.flat", debug=True)
DEBUG: found document boundary on line 1
DEBUG: found form description on line 2
DEBUG: found TCN on1347755731 on line 4
DEBUG: found an OCLC number (987654321) on line 6
DEBUG: found an 035 on line 7 (.035.   |a(Sirsi) 111111111)
DEBUG: found an OCLC number (77777777) on line 8
*warning, TCN on1347755731 contains multiple OCLC numbers. Only the last will be checked and updated as necessary.
1 OCLC updates possible from 1 records read.

>>> flat = Flat("../test_data/test2.flat", debug=True)
DEBUG: found document boundary on line 1
DEBUG: found form description on line 2
DEBUG: found TCN ocn779882439 on line 4
DEBUG: found an 035 on line 11 (.035.   |a(Sirsi) o779882439)
DEBUG: found an 035 on line 12 (.035.   |a(Sirsi) o779882439)
DEBUG: found an OCLC number (779882439) on line 13
DEBUG: found an 035 on line 14 (.035.   |a(CaAE) o779882439)
DEBUG: found document boundary on line 45
DEBUG: found form description on line 46
DEBUG: found TCN ocn782078599 on line 48
DEBUG: found an 035 on line 57 (.035.   |a(Sirsi) o782078599)
DEBUG: found an 035 on line 58 (.035.   |a(Sirsi) o782078599)
DEBUG: found an OCLC number (782078599) on line 59
DEBUG: found an 035 on line 60 (.035.   |a(CaAE) o782078599)
2 OCLC updates possible from 2 records read.

>>> flat = Flat("../test_data/test3.flat", debug=True)
DEBUG: found document boundary on line 1
DEBUG: found form description on line 2
DEBUG: found TCN ocn779882439 on line 4
DEBUG: found an 035 on line 11 (.035.   |a(Sirsi) o12345678)
DEBUG: found an 035 on line 12 (.035.   |a(Sirsi) o11111111)
DEBUG: found an 035 on line 13 (.035.   |a(CaAE) o779882439)
DEBUG: found document boundary on line 44
rejecting ocn779882439, no OCLC number.
DEBUG: found form description on line 45
DEBUG: found TCN ocn782078599 on line 47
DEBUG: found an 035 on line 56 (.035.   |a(Sirsi) o782078599)
DEBUG: found an OCLC number (987654321) on line 57
DEBUG: found an 035 on line 58 (.035.   |a(CaAE) o782078599)
DEBUG: found document boundary on line 97
DEBUG: found form description on line 98
DEBUG: found TCN epl01318816 on line 100
DEBUG: found an 035 on line 104 (.035.   |a(Sirsi) a1002054)
DEBUG: found an OCLC number (745979831) on line 105
DEBUG: found an OCLC number (777777777) on line 106
DEBUG: found an 035 on line 107 (.035.   |a(ULS) epl01318816)
*warning, TCN epl01318816 contains multiple OCLC numbers. Only the last will be checked and updated as necessary.
2 OCLC updates possible from 3 records read.
1 records were rejected because they didn't have OCLC numbers.


Test update_and_write_slim_flat() method
Given the flat file '../test_data/test.flat'
the method should generate a well formed
slim flat record.

>>> flat = Flat("../test_data/test.flat", debug=True)
DEBUG: found document boundary on line 1
DEBUG: found form description on line 2
DEBUG: found TCN on1347755731 on line 4
DEBUG: found an OCLC number (987654321) on line 6
DEBUG: found an 035 on line 7 (.035.   |a(Sirsi) 111111111)
DEBUG: found an OCLC number (77777777) on line 8
*warning, TCN on1347755731 contains multiple OCLC numbers. Only the last will be checked and updated as necessary.
1 OCLC updates possible from 1 records read.

Should return False if there were no update requests from OCLC.

>>> updated_from_log_dict = {}
>>> flat.update_and_write_slim_flat(updated_from_log_dict)
No OCLC updates detected.
False

If the dictionary contains old OCLC update requests, that is
responses from previous submissions, they should be ignored.

>>> updated_from_log_dict = {'66666666': '1010123456'}
>>> flat.update_and_write_slim_flat(updated_from_log_dict)
Ignoring '66666666' because it is not included in the submitted flat file.
No bibs records needed updating.
False

Otherwise if an update request from OCLC was found in the
logs then update and output a slim flat file.

>>> updated_from_log_dict = {'77777777': '1010123456'}
>>> flat.update_and_write_slim_flat(updated_from_log_dict)
Total flat records submitted: 1
OCLC request-to-update responses: 1
Total bib updates written to ../test_data/test.flat.updated: 1
True

Test the is_reject_record() method works for record with 250 tag ignoring case.
>>> flat = Flat("../test_data/test4.flat", debug=False, ignore={'250':'ON-ORDER'})
record on1347755731 rejected because 250 contains 'ON-ORDER'
0 OCLC updates possible from 1 records read.

Test record passes if the ignore dictionary is empty
>>> flat = Flat("../test_data/test4.flat", debug=False, ignore={})
1 OCLC updates possible from 1 records read.

Test record passes if record doesn't contain the / a reject tag.
>>> flat = Flat("../test_data/test4.flat", debug=False, ignore={'999':'e-resource'})
1 OCLC updates possible from 1 records read.


Test reading a record that already contains subfields of old OCLC numbers.

>>> flat = Flat("../test_data/test5.flat", debug=True)
DEBUG: found document boundary on line 1
DEBUG: found form description on line 2
DEBUG: found TCN on1347755731 on line 4
DEBUG: found an OCLC number (769428891) on line 6
DEBUG: found an 035 on line 7 (.035.   |a(Sirsi) 111111111)
DEBUG: found an 035 on line 9 (.035.   |a(EPL)on1347755731)
1 OCLC updates possible from 1 records read.

>>> flat = Flat("../test_data/test6.flat", debug=False, ignore={'250':'Expected release'})
rejecting ocn11111111111, no OCLC number.
record epl4444444444 rejected because 250 contains 'Expected release'
2 OCLC updates possible from 4 records read.