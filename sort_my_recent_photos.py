# Written by Aleksandr Mikheev
# https://github.com/RandyRomero/sortMyRecentPhotos
# Script that can sort out your photos and put it in folders by year and month.
# Full information via link above.

import copy
from datetime import datetime
import exifread
from os import mkdir, listdir
from os.path import exists, isfile, join, getsize
import shelve
import shutil
import sys
import collections
import re

was_copied = 0  # Global variables to count files in different functions
already_exist = 0
source_folder = ''
destination_folder = ''


def let_user_choose_folders():
    global source_folder
    global destination_folder
    while True:
        source_folder = input('Please, type in full path of folder with unsorted photos:\n')
        if exists(source_folder):
            print('Got it!')
        else:
            print('This folder doesn\'t exist. Choose another one.')
            continue

        destination_folder = input('Please, type in full path of folder where to put sorted photos:\n')
        if exists(destination_folder):
            print('Got it!')
            log = open(join(destination_folder, 'log_file.txt'), 'w')
            log.write('Source folder is ' + source_folder)
            log.write('Destination folder is ' + destination_folder)
            break
        else:
            print('This folder doesn\'t exist. Choose another one.')
            continue
    return log

log_file = let_user_choose_folders()


def prlog(message):  # function to print to console and log to file simultaneously
    print(message)
    log_file.write(message + '\n')


def sizes(files):

    total_size = 0
    for file in files:
        size = getsize(join(source_folder, file))
        total_size += size
    return total_size / 1024 / 1024


def print_and_log_files_by_ext(ilk, list_files):  # log files by extension
    prlog('Total number of ' + ilk + ' files is ' + str(len(list_files)) + '.')
    prlog('Total size of ' + ilk + ' files is ' + str('%0.2f' % sizes(list_files)) + ' MB.\n')
    log_file.write('\nList of ' + ilk + ' files:\n')
    if len(list_files) < 1:
        log_file.write('empty\n')
    else:
        for file in list_files:
            log_file.write(file + '\n')


def check_already_sorted_files():
    # Check if there are files that were already sorted in order not to sort them again
    global syncDB

    if exists(join(source_folder, '_sync')):  # if there is a DB in folder where are files to sort out
        log_file.write(join(source_folder, '_sync') + ' exists.\n')
        syncDB = shelve.open(join(source_folder, '_sync', 'filesyncDB'))  # open DB
        try:  # load from shelve list of file names that have been ever sorted in this specific source folder
            sorted_before = syncDB['as']
            log_file.write('List of files has been already in the DB\n')
        except KeyError:
            # There is no list of previously sorted files, create it
            print('Database doesn\'t have list of previously sorted files')
            sorted_before = []
            syncDB['as'] = sorted_before

    else:  # if there is no folder with DB in folder of unsorted files
        log_file.write(join(source_folder, '_sync') + ' doesn\'t exist\n')
        mkdir(join(source_folder, '_sync'))  # create folder
        syncDB = shelve.open(join(source_folder, '_sync', 'filesyncDB'))  # create DB
        sorted_before = []
        syncDB['as'] = sorted_before

    log_file.write('Getting list with names of files in ' + source_folder + '\n\n')

    sorted_before = syncDB['as']
    all_unsorted_files = [file for file in listdir(source_folder) if isfile(join(source_folder, file))]

    # create new list by 'list comprehension'. If item from all_unsorted_files
    # not in alreadySorted it appends to without_already_sorted
    without_already_sorted_files = [x for x in all_unsorted_files if x not in sorted_before]

    # get number of already sorted files
    num_already_sorted = len(all_unsorted_files) - len(without_already_sorted_files)

    # number of all unsorted files (-1 because of _sync folder)
    num_without_already_sorted_files = len(without_already_sorted_files)

    if num_already_sorted == 0:
        prlog('\nHere are ' + str(num_without_already_sorted_files) + ' unsorted files in ' + source_folder)
    else:
        prlog('\nHere are ' + str(num_without_already_sorted_files) + ' unsorted files but ' + str(num_already_sorted)
              + ' already sorted in ' + source_folder + '\n')

        # Figure out files that were sorted last time and were not removed from source folder
        already_sorted_not_removed_yet = [x for x in all_unsorted_files if x in sorted_before]

        log_file.write('Here is list of already sorted files: \n')
        for item in already_sorted_not_removed_yet:
            log_file.write(item + '\n')

    return num_without_already_sorted_files, num_already_sorted, without_already_sorted_files


def sort_by_ext_engine(without_already_sorted_files):  # sort out files by extension

    jpg_list, png_list, video_list, other_list = ([] for i in range(4))  # the way to declare multiple lists

    log_file.write('Start to sort files by extension...\n\n')

    video_ext_tuple = ('.MP4', '.3GP', '.MOV', '.mp4', '.3gp', '.mov')
    for item in without_already_sorted_files:
        item_lower = item.lower()
        if item_lower.endswith('.png'):
            png_list.append(item)
        elif item_lower.endswith('.jpg') or item_lower.endswith('.jpeg'):
            jpg_list.append(item)
        elif item_lower.endswith(video_ext_tuple):
            video_list.append(item)
        elif item == '_sync':  # skip folder with database
            continue
        else:
            other_list.append(item)

    # Use OrderedDict to preserve insertion order.
    # Python 3.6 default dict can do it out of box but I want to keep compatibility with older versions
    ext_lists = collections.OrderedDict([('JPG', jpg_list),
                                        ('PNG', png_list),
                                        ('video', video_list),
                                        ('other', other_list)])

    # Prints and logs to file list and amount of files by their extension
    for k, v in ext_lists.items():
        print_and_log_files_by_ext(k, v)

    return ext_lists


def sort_by_date(ext_lists):
    """
    Sort photos with regex by there date and put them in structure of dicts and lists that represent years and months

    :param ext_lists: ordered dict where key is a file extension or type of file,
    value is array of all file names (without paths) or files of that type or with this extension
    :return: list of files that were nit sorted; dict where key is a year and value is another dict with twelve month
    as a lists with names of files inside them
    """

    def add_photo_to_dict(filename, file_year, file_month):
        """
        Add photo to special structure
        :param filename: name of file like '2017-11-21 09-34-09.JPG' - string
        :param file_year: year like '2015' - integer
        :param file_month: month like
        :return: nothing
        """
        if file_year not in year_list:
            year_list.append(file_year)
            # Create dictionary key for every necessary year and tie its with
            # value that's a new DEEPCOPY of twelve_month. Without deepcopy we get
            # same lists of files in every year
            year_dict['{}'.format(file_year)] = copy.deepcopy(twelve_month)
        year_dict[file_year][file_month].append(filename)
        log_file.write('\nFile {} was added to year_dict[{}][{}]\n'.format(filename, file_year, file_month))

    year_list = []
    log_file.write('\nCompile regex for dates in files...\n')
    date_regex = re.compile(r''' 
        ^((?:201[0-9]))- 		# year - Group 1
        ((?:[0-1])(?:\d))-		# month - Group 2
        ((?:[0-3])(?:\d))		# day - Group 3
        .*$ 					# all other symbols after
        
        ''',
                            re.VERBOSE)

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

    # Figure out date of photo, create dict with corresponding year and add this photo inside
    # this year and corresponding month
    for k, v in ext_lists.items():
        if k == 'PNG' or k == 'other':  # k is name of list
                continue
        for item in v:  # v is list of files
            # Figure out date of photo by it's name and regex
            mo = date_regex.search(item)
            if mo:
                photo_year = mo.group(1)  # return year from photo's name
                photo_month = mo.group(2)  # return month from photo's name
                add_photo_to_dict(item, photo_year, photo_month)
                log_file.write('Date of {} was figured out by regex.'.format(item))
            else:
                # Figure out date of photo by data from EXIF
                file = open(join(source_folder, item), 'rb')
                tags = exifread.process_file(file, details=False)
                if tags.get('EXIF DateTimeOriginal') is not None:
                    date_string = str(tags['EXIF DateTimeOriginal'])
                    date = datetime.strptime(date_string, '%Y:%m:%d %H:%M:%S')
                    photo_year = str(date.year)
                    photo_month = str(date.month).rjust(2, '0')
                    add_photo_to_dict(item, photo_year, photo_month)
                    log_file.write('Date of {} was figured out by EXIF.'.format(item))
                else:
                    if k == 'video':  # if there is video without date in its name do not add it in mismatched
                        continue
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
    for yearDictKey in sorted(year_dict):
        for monthDictKey, monthDictValue in year_dict[yearDictKey].items():
            if len(monthDictValue) != 0:
                print('{} file(s) were created in {} of {}.'.format(str(len(monthDictValue)),
                                                                    month_to_print[monthDictKey], yearDictKey))
                log_file.write('\n\n{} file(s) were created in {} of {}: \n'.format(str(len(monthDictValue)),
                                                                                    month_to_print[monthDictKey],
                                                                                    yearDictKey))
            for file in monthDictValue:
                log_file.write(file + '\n')

    if len(mismatched_files) > 0:
        prlog('\nThere are ' + str(len(mismatched_files)) + ' mismatched files.\n' +
              'They will be copied in folder named "Mismatched".')
        for file in mismatched_files:  # message about mismatched files
            log_file.write(file + '\n')

    return mismatched_files, year_dict


def copy_without_date(name, files):
    # copy files that were not sorted by date

    global was_copied
    global already_exist

    log_file.write('Copy ' + name + ' files...\n\n')
    print('Copy ' + name + ' files...\n')

    already_sorted = syncDB['as']  # get list of already sorted files

    if exists(join(destination_folder, name)):
        prlog('Warning: folder "' + name + '"" in destination folder already exists')
    else:
        mkdir(join(destination_folder, name))
    for item in files:
        if exists(join(destination_folder, name, item)):
            log_file.write('Error: ' + item + ' is already in ' + name + '\n')
            already_sorted.append(item)
            already_exist += 1  # count skipped files
            continue
        else:
            shutil.copy2(join(source_folder, item), join(destination_folder, name, item))  # copy file
            was_copied += 1
            if item not in already_sorted:
                already_sorted.append(item)
            # log which and where to file was copied
            log_file.write(join(source_folder, item) + ' copy to '
                           + join(destination_folder, name, item) + '\n')

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

    for year_dict_key in sorted(files_to_copy_by_date):  # make folder for year if it hasn't existed yet
        if not exists(join(destination_folder, year_dict_key)):
            mkdir(join(destination_folder, year_dict_key))
            log_file.write(join(destination_folder, year_dict_key) + ' was created\n')

        # make folder for month if it hasn't existed yet
        for month_dict_key, month in files_to_copy_by_date[year_dict_key].items():
            path_to_month = join(destination_folder, year_dict_key, month_to_print[month_dict_key])
            if not exists(path_to_month) and len(month) != 0:
                mkdir(path_to_month)
                print('Now copy to ' + path_to_month + '...')
                log_file.write(path_to_month + ' was created\n')
            elif exists(path_to_month) and len(month) != 0:
                prlog('\nNow copy to ' + path_to_month + '...')

            # copy files by year and month
            for file in month:
                old_path_to_file = join(source_folder, file)
                new_path_to_file = join(destination_folder, year_dict_key, month_to_print[month_dict_key], file)
                if exists(new_path_to_file):
                    prlog('Warning: ' + file + ' already exists.')
                    already_sorted.append(file)
                    already_exist += 1  # count skipped files
                else:
                    shutil.copy2(old_path_to_file, new_path_to_file)
                    was_copied += 1
                    if file not in already_sorted:
                        already_sorted.append(file)
                    log_file.write(old_path_to_file + ' copy to ' + new_path_to_file + '\n')

    prlog('\nCopying of files is finished!!')

    syncDB['as'] = already_sorted


def print_log_what_was_copied(num_without_already_sorted):  # print and log what was already copied
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


def start_copying_menu(num_without_already_sorted, list_by_extensions, files_by_date):
    # Menu to ask user to start copying

    while True:
        prlog('\n\n' + str(num_without_already_sorted) + ' files are ready to copy.')
        prlog('Destination is: ' + destination_folder)

        start = input('Start? (y/n)\nYour answer is: ')
        log_file.write('Start? (y/n)\nYour answer is: ')
        if start == 'y':
            log_file.write('Got "y".\n\n')

            # Part for copying files regardless of date
            num_other_files = (len(list_by_extensions['PNG']) +
                               len(list_by_extensions['other']) + len(list_by_extensions['mismatched']))

            # Call copy_without_date_engine for specific file lists if them isn't empty
            if num_other_files > 0:
                for k, v in list_by_extensions.items():
                    if k == 'JPG' or k == 'video' or len(v) < 1:
                        continue
                    else:
                        log_file.write('\ncopyWithoutDate was invoked\n')
                        copy_without_date(k, v)

            copy_engine(files_by_date)
            print_log_what_was_copied(num_without_already_sorted)
            break
        elif start == 'n':
            log_file.write('Got "n". Exit script.\n\n')
            print('Goodbye')
            sys.exit()
        else:
            log_file.write('Got wrong input. Ask again...\n\n')
            print('Input error. You should type in y or n.')
        continue


def start_analyzing_menu():
    # Menu that start (or not) analyzing and copying
    log_file.write('Shall I start to analyze your files? (y/n)\n\n')
    while True:
        start = input('\nShall I start to analyze your files? (y/n)\nYour answer is: ')
        if start == 'y':
            # Get list of files that have not been sorted out yet
            num_without_already_sorted, num_already_sorted_files, without_already_sorted = \
                check_already_sorted_files()

            if num_without_already_sorted > 0:  # figuring out total size of all unsorted files
                log_file.write('Call sizes()\n\n')
                log_file.write('Start to figuring out total size of unsorted files\n\n')
                total_size = sizes(without_already_sorted)
                prlog('\nTotal size of ' + str(num_without_already_sorted) + ' files is '
                      + str("%0.2f" % total_size) + ' MB\n')
                dict_by_extensions = sort_by_ext_engine(without_already_sorted)
                mismatched_files, files_by_date = sort_by_date(dict_by_extensions)
                dict_by_extensions['mismatched'] = mismatched_files
                start_copying_menu(num_without_already_sorted, dict_by_extensions, files_by_date)
                break
            else:
                print('There is nothing to sort out.')
                break
        elif start == 'n':
            log_file.write('Got "n". Exit script.\n\n')
            print('Goodbye')
            sys.exit()
        else:
            log_file.write('Got wrong input. Ask again...\n\n')
            print('Input error. You should type in y or n')
            continue

start_analyzing_menu()

syncDB.close()
syncDB = None  # Workaround for some python bug with closing shelve
log_file.write('\nProgram has reached end. Closing logFile.')
log_file.close()

# ^((?:201[0-9]))-((?:0|1)(?:[0-9]))-((?:[0-3])(?:[0-9])).*$
