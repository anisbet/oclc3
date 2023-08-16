>>> from listutils import SimpleListFile, OclcCsvListFile, FlatListFile


Test reading simple lists of number possibly with extra confounding information.
>>> simple = SimpleListFile("../test_data/r1.lst", debug=True)
DEBUG: reading ../test_data/r1.lst
>>> simple.get_add_list()
['+111111', '+222222', '+333333']
>>> simple.get_delete_list()
['-111111', '-222222', '-333333']
>>> simple = SimpleListFile("../test_data/t.lst", debug=True)
DEBUG: reading ../test_data/t.lst
>>> simple.get_add_list()
['+12345', '+67890', '+112233', '+22122122']

Test reading a dirty list of data
>>> simple = SimpleListFile("../test_data/dirty.txt", debug=True)
DEBUG: reading ../test_data/dirty.txt
>>> simple.get_add_list()
['+123456', '+123456', '+7756632', '+7756632', '+654321', '+7756632', '+7756632', '+7756632', '+7756632']

Test reading CSV reports from OCLC.
>>> csv = OclcCsvListFile("../test_data/r1.csv", debug=True)
DEBUG: reading ../test_data/r1.csv
>>> csv.get_add_list()
['+267', '+1210', '+1834']
>>> csv.get_delete_list()
['-267', '-1210', '-1834']

Test reading a flat file for .035. OCoLC numbers.
>>> flat = FlatListFile("../test_data/test.flat", debug=True)
DEBUG: reading ../test_data/test.flat
>>> flat.get_add_list()
['+987654321', '+77777777']
>>> flat = FlatListFile("../test_data/test5.flat", debug=True)
DEBUG: reading ../test_data/test5.flat
>>> flat.get_add_list()
['+769428891']


Putting it together...
>>> from listutils import Lister
>>> list_reader = Lister("../test_data/r1.csv")
>>> list_reader.get_list('add')
['+267', '+1210', '+1834']
>>> list_reader.get_list('delete')
['-267', '-1210', '-1834']
>>> list_reader = Lister("../test_data/dirty.txt")
>>> list_reader.get_list('delete')
['-123456', '-123456', '-7756632', '-7756632', '-654321', '-7756632', '-7756632', '-7756632', '-7756632']
>>> l1 = ['+1','+2']
>>> l2 = ['-1','-2']
>>> list_reader.merge(l1,l2)
[' 1', ' 2']
>>> l1 = ['+1','+2']
>>> l2 = ['-3','-4']
>>> list_reader.merge(l1,l2)
['+1', '+2', '-3', '-4']
>>> l1 = ['+1','-2']
>>> l2 = ['-2','-4']
>>> list_reader.merge(l1,l2)
['+1', '-2', '-4']

Test that two lists that contain two values but one is to do nothing gets changed to required action.
>>> l1 = ['+1',' 2']
>>> l2 = ['-2','-4']
>>> list_reader.merge(l1,l2)
['+1', '-2', '-4']
>>> l1 = ['+1',' 2']
>>> l2 = [' 2','-4']
>>> list_reader.merge(l1,l2)
['+1', ' 2', '-4']

>>> l1 = ['+1','-2']
>>> l2 = []
>>> list_reader.merge(l1,l2)
['+1', '-2']

>>> l2 = ['+1','-2']
>>> l1 = []
>>> list_reader.merge(l1,l2)
['+1', '-2']
>>> l2 = ['+1','-2']
>>> l1 = ['+1',' 2', '-2']
>>> list_reader.merge(l1,l2)
['+1', '-2']
>>> l = list_reader.merge(l1,l2)

Test that we can write instructions to file and read them again.
>>> list_reader = Lister('../test_data/test_instructions.lst')
>>> list_reader.write_instructions(l)

Test we can read the instructions again
>>> a = list_reader.read_instruction_numbers(action='+')
>>> print(a)
['1']
>>> d = list_reader.read_instruction_numbers(action='-')
>>> print(d)
['2']

>>> list_reader = Lister('../test_data/test1.log')
>>> list_reader.get_updated_numbers()
{'10211111111': '211111111', '10222222222': '222222222', '10233333333': '233333333'}