#!python3 

import copy
import os
import shelve
import shutil
import sys
import collections
import re

list_by_extensions = []
files_by_date = []


def prlog(message):  # function to print to console and log to file simultaneously
    print(message)
    logFile.write(message + '\n')


def sizes(files):

    total_size = 0
    for file in files:
        size = os.path.getsize(os.path.join(unsorted_photos, file))
        total_size += size
    return total_size / 1024 / 1024


def print_log_files_by_ext(ilk, list_files):  # log files by extension
    prlog('Total amount of ' + ilk + ' files is ' + str(len(list_files)))
    prlog('Total size of ' + ilk + ' files is ' + str('%0.2f' % sizes(list_files)) + ' MB\n')
    logFile.write('\nList of ' + ilk + ' files:\n')
    if len(list_files) < 1:
        logFile.write('empty\n')
    else:
        for file in list_files:
            logFile.write(file + '\n')


def check_already_sorted_files():
    # Check if there are files that were already sorted in order not to sort them again
    global syncDB

    if os.path.exists(os.path.join(unsorted_photos, '_sync')):  # if there is a DB in folder where are files to sort out
        logFile.write(os.path.join(unsorted_photos, '_sync') + ' exists.\n')
        syncDB = shelve.open(os.path.join(unsorted_photos, '_sync', 'filesyncDB'))  # open DB
        try:  # extract list of file names that were already sorted last time from shelve
            already_sorted = syncDB['as']
            logFile.write('List of files has been already in the DB\n')
        except KeyError:
            # There is no list of previously sorted files, create it
            print('Database doesn\'t have list of previously sorted files')
            already_sorted = []
            syncDB['as'] = already_sorted

    else:  # if there is no folder with DB in folder of unsorted files
        logFile.write(os.path.join(unsorted_photos, '_sync') + ' doesn\'t exist\n')
        os.mkdir(os.path.join(unsorted_photos, '_sync'))  # create folder
        syncDB = shelve.open(os.path.join(unsorted_photos, '_sync', 'filesyncDB'))  # create DB
        already_sorted = []
        syncDB['as'] = already_sorted

    logFile.write('Getting list with names of files in ' + unsorted_photos + '\n\n')

    already_sorted = syncDB['as']
    all_unsorted_files = os.listdir(unsorted_photos)

    # create new list by 'list comprehension'. If item from all_unsorted_files
    # not in alreadySorted it appends to without_already_sorted
    without_already_sorted_files = [x for x in all_unsorted_files if x not in already_sorted]

    # get number of already sorted files
    num_already_sorted = len(all_unsorted_files) - len(without_already_sorted_files)

    # number of all unsorted files (-1 because of _sync folder)
    num_without_already_sorted_files = len(without_already_sorted_files) - 1

    if num_already_sorted == 0:
        prlog('\nHere are ' + str(num_without_already_sorted_files) + ' unsorted files in ' + unsorted_photos)
    else:
        prlog('\nHere are ' + str(num_without_already_sorted_files) + ' unsorted files but ' + str(num_already_sorted)
              + ' already sorted in' + unsorted_photos + '\n')

        intercept = [x for x in all_unsorted_files if x in already_sorted]

        logFile.write('Here is list of already sorted files: \n')
        for item in intercept:  # TODO change name of variable to more meaningful
            logFile.write(item + '\n')

    return num_without_already_sorted_files, num_already_sorted, without_already_sorted_files


def sort_by_ext_engine(without_already_sorted_files):  # sort out files by extension

    jpg_list, png_list, video_list, other_list = ([] for i in range(4))  # the way to declare multiple lists

    logFile.write('Start to sort files by extension...\n\n')
    for item in without_already_sorted_files:
        if item.endswith('.PNG') or item.endswith('.png'):
            png_list.append(item)
        elif item.endswith('.JPG') or item.endswith('.jpg') or item.endswith('.JPEG'):
            jpg_list.append(item)
        elif item.endswith('.MP4') or item.endswith('.3GP'):
            video_list.append(item)
        elif item == '_sync':  # skip folder with database
            continue
        else:
            other_list.append(item)

    # Use OrderedDict to preserve insertion order.
    # Python 3.6 default dict can do it from box but I want to keep compatibility with older versions
    ext_lists = collections.OrderedDict([('JPG', jpg_list),
                                        ('PNG', png_list),
                                        ('video', video_list),
                                        ('other', other_list)])

    # Prints and logs to file list and amount of files by their extension
    for k, v in ext_lists.items():
        print_log_files_by_ext(k, v)

    return ext_lists


def sort_by_date(ext_lists):
    # First we need to know home many years we have. That's why we
    # send files through regex - to get all possible years and store them
    # to list

    year_list = []
    logFile.write('\nCompile regex for dates in files...\n')
    date_regex = re.compile(r''' 
        ^((?:201[0-9]))- 		# year - Group 1
        ((?:[0-1])(?:\d))-		# month - Group 2
        ((?:[0-3])(?:\d))		# day - Group 3
        .*$ 					# all other symbols after
        
        ''',
                            re.VERBOSE)

    for k, v in ext_lists.items():
        if k == 'PNG' or k == 'already sorted':  # k is name of list
                continue
        for item in v:  # v is list of files
            mo = date_regex.search(item)
            if mo is not None:
                year_num = mo.group(1)  # return year from file name
                if year_num not in year_list:
                    year_list.append(year_num)

    # Now we need a dictionary in order to get specific group of month
    # by passing a year
    year_dict = collections.OrderedDict([])

    # declare 12 empty lists for each month — one for each month
    january, february, march, april = ([] for i in range(4))
    may, june, july, august = ([] for i in range(4))
    september, october, november, december = ([] for i in range(4))

    twelve_month = collections.OrderedDict([])
    twelve_month['01'] = january
    twelve_month['02'] = february
    twelve_month['03'] = march
    twelve_month['04'] = april
    twelve_month['05'] = may
    twelve_month['06'] = june
    twelve_month['07'] = july
    twelve_month['08'] = august
    twelve_month['09'] = september
    twelve_month['10'] = october
    twelve_month['11'] = november
    twelve_month['12'] = december

    mismatched_files = []  # for files that do not match regex

    # Create dictionary key for every necessary year and tie its with
    # value that's a new DEEPCOPY of twelve_month. Without deepcopy we get
    # same lists of files in every year
    for year in year_list:
        year_dict['{}'.format(year)] = copy.deepcopy(twelve_month)

    for k, v in ext_lists.items():
        if k == 'PNG' or k == 'already sorted':  # k is name of extension
                continue
        for item in v:  # v is list of files
            mo = date_regex.search(item)
            if mo is not None:
                # Add file to corresponding location e.g.: year 2016 month january
                year_dict[mo.group(1)][mo.group(2)].append(item)
                logFile.write('\nFile ' + item + ' was added to ' + 'year_dict[' + mo.group(1) + '][' +
                              mo.group(2) + ']')
            else:
                mismatched_files.append(item)

    month_to_print = {'01': 'January',
                      '02': 'February',
                      '03': 'March',
                      '04': 'April',
                      '05': 'May',
                      '06': 'June',
                      '07': 'July',
                      '08': 'August',
                      '09': 'September',
                      '10': 'October',
                      '11': 'November',
                      '12': 'December'}

    print('\nSorted out by date:')
    # print out and log list of photos and videos by month and year
    for yearDictKey, yearDictValue in year_dict.items():
        for monthDictKey, monthDictValue in yearDictValue.items():
            if len(monthDictValue) != 0:
                print(str(len(monthDictValue)) + ' file was created in ' + month_to_print[monthDictKey] +
                      ' of ' + yearDictKey + '.')
                logFile.write('\n\n' + str(len(monthDictValue)) + ' file was created in ' +
                              month_to_print[monthDictKey] + ' of ' + yearDictKey + ': \n')
            for file in monthDictValue:
                logFile.write(file + '\n')

    if len(mismatched_files) > 0:
        prlog('\nThere are ' + str(len(mismatched_files)) + ' mismatched files.\n' +
              'They will be copied in folder named "Mismatched".')
        for file in mismatched_files:  # message about mismatched files
            logFile.write(file + '\n')

    return mismatched_files, year_dict


def copy_without_date(name, files):
    # copy files that were not sorted by date

    global was_copied
    global already_exist

    logFile.write('Copy ' + name + ' files...\n\n')
    print('Copy ' + name + ' files...\n')

    already_sorted = syncDB['as']  # get list of already sorted files

    if os.path.exists(os.path.join(sorted_photos, name)):
        prlog('Warning: folder "' + name + '"" in destination folder already exists')
    else:
        os.mkdir(os.path.join(sorted_photos, name))
    for item in files:
        if os.path.exists(os.path.join(sorted_photos, name, item)):
            logFile.write('Error: ' + item + ' is already in ' + name + '\n')
            already_sorted.append(item)
            already_exist += 1  # count skipped files
            continue
        else:
            shutil.copy2(os.path.join(unsorted_photos, item), os.path.join(sorted_photos, name, item))  # copy file
            was_copied += 1
            if item not in already_sorted:
                already_sorted.append(item)
            # log which and where to file was copied
            logFile.write(os.path.join(unsorted_photos, item) + ' copy to ' + os.path.join(sorted_photos, name, item) +
                          '\n')

    syncDB['as'] = already_sorted


def copy_engine(files_to_copy_by_date):
    # copy files according their year and month
    prlog('\nStart to copy photo and video by date...')

    global was_copied
    global already_exist

    already_sorted = syncDB['as']  # get list of already sorted files

    month_to_print = {'01': '[01] January',
                      '02': '[02] February',
                      '03': '[03] March',
                      '04': '[04] April',
                      '05': '[05] May',
                      '06': '[06] June',
                      '07': '[07] July',
                      '08': '[08] August',
                      '09': '[09] September',
                      '10': '[10] October',
                      '11': '[11] November',
                      '12': '[12] December'}

    for year_dict_key, year in files_to_copy_by_date.items():  # make folder for year if it hasn't existed yet
        if not os.path.exists(os.path.join(sorted_photos, year_dict_key)):
            os.mkdir(os.path.join(sorted_photos, year_dict_key))
            logFile.write(os.path.join(sorted_photos, year_dict_key) + ' was created\n')

        for month_dict_key, month in year.items():  # make folder for month if it hasn't existed yet
            path_to_month = os.path.join(sorted_photos, year_dict_key, month_to_print[month_dict_key])
            if not os.path.exists(path_to_month) and len(month) != 0:
                os.mkdir(path_to_month)
                print('Now copy to ' + path_to_month + '...')
                logFile.write(path_to_month + ' was created\n')
            elif os.path.exists(path_to_month) and len(month) != 0:
                prlog('\nNow copy to ' + path_to_month + '...')

            # copy files by year and month
            for file in month:
                old_path_to_file = os.path.join(unsorted_photos, file)
                new_path_to_file = os.path.join(sorted_photos, year_dict_key, month_to_print[month_dict_key], file)
                if os.path.exists(new_path_to_file):
                    prlog('Warning: ' + file + ' already exists.')
                    already_sorted.append(file)
                    already_exist += 1  # count skipped files
                else:
                    shutil.copy2(old_path_to_file, new_path_to_file)
                    was_copied += 1
                    if file not in already_sorted:
                        already_sorted.append(file)
                    logFile.write(old_path_to_file + ' copy to ' + new_path_to_file + '\n')

    prlog('\nCopying of files is finished!!')

    syncDB['as'] = already_sorted


def was_copied_engine():  # print and long what was copied
    global was_copied
    global already_exist

    if was_copied > 0:
        prlog('\n' + str(was_copied) + ' files were copied')
        if already_exist == 1:
            prlog('There is 1 skipped file')
        elif already_exist > 1:
            prlog(str(already_exist) + ' files were skipped')
        elif already_exist == 0:
            prlog('There are no skipped files')
    else:
        prlog('All files (' + str(already_exist) + ' from ' + str(num_without_already_sorted) +
              ') already exist in destination folder')

if os.path.exists(os.path.join('D:/', 'PythonPhoto', 'sortedPhotos')):  # check if folder for work exist
    # mind the syntax: it is 'D:/', neither 'd', nor 'D:', nor "D:/"

    logFile = open('D:\\PythonPhoto\\sortedPhotos\\logFile.txt', 'w')
    logFile.write('Program started. Log file was created.\n\n')
    sorted_photos = 'D:\\PythonPhoto\\sortedPhotos'
    logFile.write('Path to main folders was created\n\n')
else:
    prlog(os.path.join('D:/', 'PythonPhoto', 'sortedPhotos') + ' doesn\'t exist')
    sys.exit()

if os.path.exists(os.path.join('D:/', 'PythonPhoto', 'unsortedPhotos')):
    unsorted_photos = 'D:\\PythonPhoto\\unsortedPhotos'
else:
    prlog(os.path.join('D:/', 'PythonPhoto', 'sortedPhotos') + ' doesn\'t exist')
    sys.exit()

# First menu
logFile.write('Shall I start to analyze your files? (y/n)\n\n')

while True:
    start = input('\nShall I start to analyze your files? (y/n)\nYour answer is: ')
    if start == 'y':
        logFile.write('Got "y". Call sortByExtEngine()\n\n')
        num_without_already_sorted, num_already_sorted, without_already_sorted = \
            check_already_sorted_files()

        if num_without_already_sorted > 0:  # figuring out total size of all unsorted files
            logFile.write('Call sizes()\n\n')
            logFile.write('Start to figuring out total size of unsorted files\n\n')
            totalSize = sizes(without_already_sorted)
            prlog('\nTotal size of ' + str(num_without_already_sorted) + ' files is '
                  + str("%0.2f" % totalSize) + ' MB\n')
            list_by_extensions = sort_by_ext_engine(without_already_sorted)
            mismatched_files, files_by_date = sort_by_date(list_by_extensions)
            list_by_extensions['mismatched'] = mismatched_files
            break
        else:
            print('There is nothing to sort out.')
            break
    elif start == 'n':
        logFile.write('Got "n". Exit script.\n\n')
        print('Goodbye')
        sys.exit()
    else:
        logFile.write('Got wrong input. Ask again...\n\n')
        print('Input error. You should type in y or n')
        continue

# Menu to ask user to start copying
if num_without_already_sorted > 0:  # if there is anything to copy
    while True:
        prlog('\n\n' + str(num_without_already_sorted) + ' files are ready to copy.')
        prlog('Destination is: ' + sorted_photos)

        start = input('Start? (y/n)\nYour answer is: ')
        logFile.write('Start? (y/n)\nYour answer is: ')
        if start == 'y':
            logFile.write('Got "y".\n\n')
            was_copied = 0  # Global variables to count files in different functions
            already_exist = 0

            # Part for copying files regardless of date
            numOtherFiles = (len(list_by_extensions['PNG']) +
                             len(list_by_extensions['other']) + len(list_by_extensions['mismatched']))

            # Call copy_without_date_engine for specific file lists if them isn't empty
            if numOtherFiles > 0:
                for k, v in list_by_extensions.items():
                    if k == 'JPG' or k == 'video' or len(v) < 1:
                        continue
                    else:
                        logFile.write('\ncopyWithoutDate was invoked\n')
                        copy_without_date(k, v)

            copy_engine(files_by_date)
            was_copied_engine()
            break
        elif start == 'n':
            logFile.write('Got "n". Exit script.\n\n')
            print('Goodbye')
            sys.exit()
        else:
            logFile.write('Got wrong input. Ask again...\n\n')
            print('Input error. You should type in y or n.')
        continue
else:
    prlog('There are no files to copy. Bye.')

syncDB.close()
syncDB = None  # Workaround for some python bug with closing shelve
logFile.write('\nProgram has reached end. Closing logFile.')
logFile.close()

# ^((?:201[0-9]))-((?:0|1)(?:[0-9]))-((?:[0-3])(?:[0-9])).*$
