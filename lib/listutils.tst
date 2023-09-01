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
DEBUG: found document boundary on line 1
DEBUG: found form description on line 2
DEBUG: found TCN on1347755731 on line 4
DEBUG: found an OCLC number (987654321) on line 6
DEBUG: found an 035 on line 7 (.035.   |a(Sirsi) 111111111)
DEBUG: found an OCLC number (77777777) on line 8
*warning, TCN on1347755731 contains multiple OCLC numbers. Only the last will be checked and updated as necessary.
1 OCLC updates possible from 1 records read.
>>> flat.get_add_list()
['+77777777']
>>> flat = FlatListFile("../test_data/test5.flat", debug=True)
DEBUG: reading ../test_data/test5.flat
DEBUG: found document boundary on line 1
DEBUG: found form description on line 2
DEBUG: found TCN on1347755731 on line 4
DEBUG: found an OCLC number (769428891) on line 6
DEBUG: found an 035 on line 7 (.035.   |a(Sirsi) 111111111)
DEBUG: found an 035 on line 9 (.035.   |a(EPL)on1347755731)
1 OCLC updates possible from 1 records read.
>>> flat.get_add_list()
['+769428891']


Putting it together...
>>> from listutils import Lister
>>> list_reader = Lister("../test_data/test5.flat")
1 OCLC updates possible from 1 records read.
>>> list_reader = Lister("../test_data/r1.csv")
>>> list_reader.get_list('+')
['+267', '+1210', '+1834']
>>> list_reader.get_list('-')
['-267', '-1210', '-1834']
>>> list_reader = Lister("../test_data/dirty.txt")
>>> list_reader.get_list('-')
['-123456', '-123456', '-7756632', '-7756632', '-654321', '-7756632', '-7756632', '-7756632', '-7756632']

Test InstructionManager
>>> from listutils import InstructionManager
>>> instructor = InstructionManager('someFile.inst')
>>> l1 = ['+1','+2']
>>> l2 = ['-1','-2']
>>> instructor.merge(l1,l2)
[' 1', ' 2']
>>> l1 = ['+1','+2']
>>> l2 = ['-3','-4']
>>> instructor.merge(l1,l2)
['+1', '+2', '-3', '-4']
>>> l1 = ['+1','-2']
>>> l2 = ['-2','-4']
>>> instructor.merge(l1,l2)
['+1', '-2', '-4']

Test that two lists that contain two values but one is to do nothing gets changed to required action.
>>> l1 = ['+1',' 2']
>>> l2 = ['-2','-4']
>>> instructor.merge(l1,l2)
['+1', '-2', '-4']
>>> l1 = ['+1',' 2']
>>> l2 = [' 2','-4']
>>> instructor.merge(l1,l2)
['+1', ' 2', '-4']

>>> l1 = ['+1','-2']
>>> l2 = []
>>> instructor.merge(l1,l2)
['+1', '-2']

>>> l2 = ['+1','-2']
>>> l1 = []
>>> instructor.merge(l1,l2)
['+1', '-2']
>>> l2 = ['+1','-2']
>>> l1 = ['+1',' 2', '-2']
>>> instructor.merge(l1,l2)
['+1', '-2']
>>> l = instructor.merge(l1,l2)

Test that instructions to add or delete are overridden by done list
>>> l2 = ['+1','-2', '!3']
>>> l1 = ['!1','!2', '+3']
>>> instructor.merge(l1,l2)
['!1', '!2', '!3']

>>> l2 = ['+1','-2', '!3']
>>> l1 = ['!1','!2', '+3', ' 4']
>>> instructor.merge(l1,l2)
['!1', '!2', '!3', ' 4']

>>> l1 = ['+1','-2', '!3']
>>> l2 = ['!1','!2', '+3', ' 4']
>>> instructor.merge(l1,l2)
['!1', '!2', '!3', ' 4']

>>> l2 = ['+1','-2', '!3']
>>> l1 = ['!1','!2', '+3', '?4']
>>> instructor.merge(l1,l2)
['!1', '!2', '!3', '?4']
>>> l1 = ['+1','-2', '!3', ' 4']
>>> l2 = ['!1','!2', '+3', '?4']
>>> instructor.merge(l1,l2)
['!1', '!2', '!3', '?4']
>>> l2 = ['+1','-2', '!3', ' 4']
>>> l1 = ['!1','!2', '+3', '?4']
>>> instructor.merge(l1,l2)
['!1', '!2', '!3', '?4']
>>> l2 = ['+1','-2', '!3', ' 4']
>>> l1 = ['+5','-6', '!7', '?8']
>>> instructor.merge(l1,l2)
['+1', '-2', '!3', ' 4', '+5', '-6', '!7', '?8']

Test that we can write instructions to file and read them again.
>>> instructor = InstructionManager('../test_data/test_instructions.lst')
>>> instructor.write_instructions(l)

Test we can read the instructions again
>>> a = instructor.read_instruction_numbers(action='+')
>>> print(a)
['1']
>>> d = instructor.read_instruction_numbers(action='-')
>>> print(d)
['2']

Test that you can get all the different list types of 'add', 'delete', 'check', 'done', and 'other' for no changes.
>>> instructor = InstructionManager('../test_data/i.lst')
>>> instructor.read_instruction_numbers(action='?')
['222222']
>>> instructor.read_instruction_numbers(action='+')
['333333']
>>> instructor.read_instruction_numbers(action='-')
['555555']
>>> instructor.read_instruction_numbers(action='!')
['666666']
>>> instructor.read_instruction_numbers(action=' ')
['444444']


Test multiple list merging
>>> a = ['+1','+2']
>>> d = ['-2', '-3']
>>> c = ['?3', '?4']
>>> f = ['!4', '!5']
>>> n = [' 5', ' 6']
>>> master = instructor.merge(a, d)
>>> master
['+1', ' 2', '-3']
>>> master = instructor.merge(master, c)
>>> master
['+1', ' 2', '?3', '?4']
>>> master = instructor.merge(master, f)
>>> master
['+1', ' 2', '?3', '!4', '!5']
>>> master = instructor.merge(master, n)
>>> master
['+1', ' 2', '?3', '!4', '!5', ' 6']

Test with all the lists.
master = instructor.merge(a, d, c, f, n)
>>> master
['+1', ' 2', '?3', '!4', '!5', ' 6']