#!python3 

import os, shutil, sys, collections, re

logFile = open('D:\\PythonPhoto\\sortedPhotos\\logFile.txt', 'w')
logFile.write('Program started. Log file created\n\n')

unsortedPhotos = ('D:\\PythonPhoto\\unsortedPhotos')
sortedPhotos = ('D:\\PythonPhoto\\sortedPhotos')
logFile.write('Path to main folders created\n\n')

################################## sizes ###############################	

def sizes(files):
	
	totalSize = 0
	for file in files:
		size = os.path.getsize(os.path.join(unsortedPhotos, file))
		totalSize += size
	return totalSize / 1024 / 1024

######################### log files by extention ###############################	

def printLogFilesByExt(ilk, listFiles):
	logFile.write('\nTotal amount of ' + ilk +' files is ' + 
		str(len(listFiles)))	
	print('Total amount of ' + ilk + ' files is ' 
		+ str(len(listFiles)))
	print('Total size of ' + ilk + ' files is ' + 
		str('%0.2f' % sizes(listFiles)) + ' MB\n')
	logFile.write('\nList of ' + ilk + ' files:\n')	
	if len(listFiles) < 1:
		logFile.write('empty\n')
	else:
		for file in listFiles:
			logFile.write(file + '\n')

############################# sort by month ##############################

def sortByMonth(extLists):

	logFile.write('Make list of month...\n\n')

	january, february, march, april = ([] for i in range(4))
	may, june, july, august = ([] for i in range(4))
	september, october, november, december = ([] for i in range(4))
	#declare 12 lists fo each month

	logFile.write('Make dict of lists of month...\n\n')
	month = collections.OrderedDict([])
	month['01'] = january
	month['02'] = february
	month['03'] = march
	month['04'] = april
	month['05'] = may
	month['06'] = june
	month['07'] = july
	month['08'] = august
	month['09'] = september
	month['10'] = october
	month['11'] = november
	month['12'] = december
	#put lists in dictionary

	logFile.write('Compile regex for dates in files...\n\n')
	dateRegex = re.compile(r''' 
		^((?:201[0-9]))- 		#year - Group 1
		((?:0|1)(?:\d))-		#month - Group 2
		((?:[0-3])(?:\d))		#day - Group 3
		.*$ 					#all other symbols after
		
		''', 
		re.VERBOSE)
	#regex to sort out files by month

	mismatchFiles = []

	for k,v in extLists.items():
		if k == 'PNG':
			continue
		
		for item in v:	
			mo = dateRegex.search(item)
			if mo != None:
				month[mo.group(2)].append(mo.group())
				#put files in lists according to their month
			else:
				mismatchFiles.append(item)
				#make list of file that didn't match regex

	for k, v in month.items():
		if len(v) > 0:
			logFile.write('Content of ' + k + ' is: \n')
			for item in v:
				logFile.write(item + '\n')
			logFile.write('\n\n')

	logFile.write('\nHere is list of unsorted files. They won\'t be copied anywhere:\n')
	print('\nHere is list of unsorted files. They won\'t be copied anywhere:')
	for file in mismatchFiles:
		print(file)
		logFile.write(file + '\n')
				

################################## copy PNG  #################################

def copyPng(listOfPng):
	for item in listOfPng:
		print(os.path.join(unsortedPhotos, item))


############################### sortByExtEngine  ##############################			

def sortByExtEngine():
	logFile.write('Getting list with names of files in ' + unsortedPhotos + 
		'\n\n')
	files = os.listdir(unsortedPhotos)

	logFile.write('There are ' + str(len(files)) + ' files in ' 
		+ unsortedPhotos + '\n\n')
	print('\nHere are ' + str(len(files)) + ' unsorted files.')
	
	###figuring out total size of all unsorted files###

	logFile.write('Call sizes()\n\n')
	logFile.write('Start to figuring out total size of unsorted files\n\n')
	totalSize = sizes(files)
	logFile.write('Total size of ' + str(len(files)) + ' files is ' 
		+ str("%0.2f" % totalSize) + ' MB\n\n')
	print('\nTotal size of ' + str(len(files)) + ' files is ' 
		+ str("%0.2f" % totalSize) + ' MB\n')

	######sort out files by extentions######
	
	jpgList, pngList, videoList, otherList = ([] for i in range(4))
	#the way to declare multiple lists

	logFile.write('Start to sort files by extension...\n\n')
	for item in os.listdir(unsortedPhotos):
		if item.endswith('.PNG') or item.endswith('.png'):
			pngList.append(item)
		elif (item.endswith('.JPG') or item.endswith('.jpg') 
			or item.endswith('.JPEG')):
			jpgList.append(item)
		elif item.endswith('.MP4') or item.endswith('.3GP'):
			videoList.append(item)
		else:
			otherList.append(item)
			print(item)

	extLists = collections.OrderedDict([('JPG', jpgList), ('PNG', pngList), 
		('video', videoList), ('other', otherList)])
	#use OrderedDict to preserve insertion order. Python 3.6 default dict can
	#do it from box but I want to keep compatibility with older versions

	for k,v in extLists.items():
		 printLogFilesByExt(k,v)
	#prints and logs to file list and amount of files by their extention	

	return extLists


########################  Begining of the program  #######################

def copyEngine(extLists):

	month = sortByMonth(extLists)
	#split files in different lists by month (skip PNG)
	# for k,v in month.items():

	


########################  Begining of the program  #######################


logFile.write('Start to look for your photos? (y/n)\n\n')

while True:
	start = input('\nStart to look for your photos? (y/n) Your answer is: ')
	if start == 'y':
		logFile.write('Got "y". Call sortByExtEngine()\n\n')
		extLists = sortByExtEngine()
		break
	elif start == 'n':
		logFile.write('Got "n". Exit script.\n\n')
		print('Goodbye')
		sys.exit()
	else:
		logFile.write('Got wrong input. Ask again...\n\n')
		print('Input error. You should type in y or n')	
		continue

######### start copy or not menu #############

while True:
	logFile.write('\nStart sort out and copy files to ' + 
		sortedPhotos + '? (y/n). You answer is: \n')
	
	readyOrNot = input('\nStart sort out and copy files to ' + 
		sortedPhotos + '? (y/n). You answer is: ')
	
	if readyOrNot == 'y':
		logFile.write('Got "y". Call sortByExtEngine()\n\n')
		copyEngine(extLists)
		break
	elif readyOrNot == "n":
		logFile.write('Got "n". Exit script.\n\n')
		print('Ok, next time. See ya')
		sys.exit()
	else:
		logFile.write('Got wrong input. Ask again...\n\n')
		print('Input error. You should type in y or n')	
		continue

logFile.write('\nProgram has reached end. Closing logFile.')
logFile.close()


#TODO comparison of sorted and unsorted in order to figure out
#if sorting went without missing any file

#TODO delete unsortedFiles by users submit after checking that unsorted 
#sorted files are equal in total quatity and size


# ^((?:201[0-9]))-((?:0|1)(?:[0-9]))-((?:[0-3])(?:[0-9])).*$