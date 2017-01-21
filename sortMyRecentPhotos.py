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

	###sort out files by extentions###
	
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

	for v in extLists.values():
		sortByMonth(v)

############################# sort by month ##############################

def sortByMonth(fileList):

	logFile.write('Make list of month...')
	january, february, march, april, may, june, july, august, september, october, november, december = ([] for i in range(12))

	logFile.write('Make dict of lists of month...')
	month = {}
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

	logFile.write('Compile regex for dates in files...')
	dateRegex = re.compile(r''' 
		^((?:201[0-9]))- 		#year - Group 1
		((?:0|1)(?:\d))-		#month - Group 2
		((?:[0-3])(?:\d))	#day - Group 3
		.*$ 					#all other symbols after
		
		''', 
		re.VERBOSE)

	imageName = ''

	for item in fileList:
		mo = dateRegex.search(item)
		if mo != None:
			month[mo.group(2)].append(mo.group())

	for k, v in month.items():
		print('Content of ' + k + ' is: ')
		print(v)
		print('\n\n')


########################  Begining of the program  #######################


logFile.write('Start to look for your photos? (y/n)\n\n')

while True:
	start = input('\nStart to look for your photos? (y/n) Your answer is: ')
	if start == 'y':
		logFile.write('Got "y". Call sortByExtEngine()\n\n')
		sortByExtEngine()
		break
	elif start == 'n':
		logFile.write('Got "n". Exit script.\n\n')
		print('Goodbye')
		sys.exit()
	else:
		logFile.write('Got wrong input. Ask again...\n\n')
		print('Input error. You should type in y or n')	
		continue

logFile.write('\nProgram has reached end. Closing logFile.')
logFile.close()		


# ^((?:201[0-9]))-((?:0|1)(?:[0-9]))-((?:[0-3])(?:[0-9])).*$