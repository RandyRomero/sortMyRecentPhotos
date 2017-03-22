#!python3 

import copy, os, shelve, shutil, sys, collections, re

def prlog(message):
	print(message)
	logFile.write(message + '\n')

################################## sizes ###############################	

def sizes(files):
	
	totalSize = 0
	for file in files:
		size = os.path.getsize(os.path.join(unsortedPhotos, file))
		totalSize += size
	return totalSize / 1024 / 1024

######################### log files by extention #########################	

def printLogFilesByExt(ilk, listFiles):
	prlog('Total amount of ' + ilk + ' files is ' 
		+ str(len(listFiles)))
	prlog('Total size of ' + ilk + ' files is ' + 
		str('%0.2f' % sizes(listFiles)) + ' MB\n')
	logFile.write('\nList of ' + ilk + ' files:\n')	
	if len(listFiles) < 1:
		logFile.write('empty\n')
	else:
		for file in listFiles:
			logFile.write(file + '\n')

######################## Check already sorted files  ####################

def checkAlreadySortedFiles(unsortedPhotos):
	global syncDB

	if os.path.exists(os.path.join(unsortedPhotos, '_sync')):
		logFile.write(os.path.join(unsortedPhotos, '_sync') + ' exists.\n')
		syncDB = shelve.open(os.path.join(unsortedPhotos, 
								'_sync', 'filesyncDB'))
		try:
			alreadySorted = syncDB['as']
		except KeyError:
			print('Database doesn\'t have list of files')
			alreadySorted = []
			syncDB['as'] = alreadySorted
		#extract list of file names from shelve
	else:
		logFile.write(os.path.join(unsortedPhotos, '_sync') + 
			' doesn\'t exist\n')
		os.mkdir(os.path.join(unsortedPhotos, '_sync'))
		syncDB = shelve.open(os.path.join(unsortedPhotos, 
								'_sync', 'filesyncDB'))
		alreadySorted = []
		syncDB['as'] = alreadySorted
		logFile.write('List of files has been already in the DB\n') 

	logFile.write('Getting list with names of files in ' + unsortedPhotos + 
		'\n\n')

	alreadySorted = syncDB['as']
	allUnsortedFiles = os.listdir(unsortedPhotos)

	withoutAlreadySorted = [x for x in allUnsortedFiles 
							if x not in alreadySorted]
	#create new list by 'list comprehension'. If item from allUnsotredFiles 
	#not in alreadySorted it appends to withoutAlreadySorted	

	numAlreadySorted = len(allUnsortedFiles) - len(withoutAlreadySorted)
	#get number of already sorted files
	
	numWithoutAlreadySorted = len(withoutAlreadySorted) - 1
	#number of all unsorted files (-1 because of _sync folder)

	if numAlreadySorted == 0:
		prlog('\nHere are ' + str(numWithoutAlreadySorted) + 
			' unsorted files in ' + unsortedPhotos)
	else:	
		prlog('\nHere are ' + str(numWithoutAlreadySorted) + 
			' unsorted files but ' + str(numAlreadySorted) 
			+ ' already sorted in' + unsortedPhotos + '\n')

		intercept = [x for x in allUnsortedFiles if x in alreadySorted]

		logFile.write('Here is list of already sorted files: \n')
		for item in intercept: #TODO change name of varibale to more meaningfull
			logFile.write(item + '\n')

	return numWithoutAlreadySorted, numAlreadySorted, withoutAlreadySorted

############################### sortByExtEngine  ##########################	

def sortByExtEngine(withoutAlreadySorted):
	
	######sort out files by extentions######
	
	jpgList, pngList, videoList, otherList = ([] for i in range(4))
	#the way to declare multiple lists


	logFile.write('Start to sort files by extension...\n\n')
	for item in withoutAlreadySorted:
		if item.endswith('.PNG') or item.endswith('.png'):
			pngList.append(item)
		elif (item.endswith('.JPG') or item.endswith('.jpg') 
			or item.endswith('.JPEG')):
			jpgList.append(item)
		elif item.endswith('.MP4') or item.endswith('.3GP'):
			videoList.append(item)
		elif item == '_sync': #skip folder with database
			continue
		else:
			otherList.append(item)

	extLists = collections.OrderedDict([('JPG', jpgList), 
										('PNG', pngList), 
										('video', videoList), 
										('other', otherList)])
	#use OrderedDict to preserve insertion order. Python 3.6 default dict can do it from box but I want to keep compatibility with older versions

	for k,v in extLists.items():
		 printLogFilesByExt(k,v)
	#prints and logs to file list and amount of files by their extention

	return extLists

############################# Sort by Date ##############################

def sortByDate(extLists):

	#First we need to know home many years we have. That's why we 
	#send files through regex - to get all possible years and store them
	#to list

	yearList = []
	logFile.write('\nCompile regex for dates in files...\n')
	dateRegex = re.compile(r''' 
		^((?:201[0-9]))- 		#year - Group 1
		((?:0|1)(?:\d))-		#month - Group 2
		((?:[0-3])(?:\d))		#day - Group 3
		.*$ 					#all other symbols after
		
		''', 
		re.VERBOSE)

	for k, v in extLists.items(): 
		if k == 'PNG' or k == 'already sorted': #k is name of list
				continue
		for item in v: #v is list of files
			mo = dateRegex.search(item)
			if mo != None:
				yearNum = mo.group(1) #return year from file name
				if yearNum not in yearList:
					yearList.append(yearNum) 

	#now we need a dictionary in order to get specific group of month
	#by passing a year
	yearDict = collections.OrderedDict([])

	january, february, march, april = ([] for i in range(4))
	may, june, july, august = ([] for i in range(4))
	september, october, november, december = ([] for i in range(4))
	#declare 12 empty lists fo each month

	twelveMonth = collections.OrderedDict([])
	twelveMonth['01'] = january
	twelveMonth['02'] = february
	twelveMonth['03'] = march
	twelveMonth['04'] = april
	twelveMonth['05'] = may
	twelveMonth['06'] = june
	twelveMonth['07'] = july
	twelveMonth['08'] = august
	twelveMonth['09'] = september
	twelveMonth['10'] = october
	twelveMonth['11'] = november
	twelveMonth['12'] = december

	mismatchedFiles = [] #for files that not match regex

	for year in yearList: 
		yearDict['{}'.format(year)] = copy.deepcopy(twelveMonth)
	#create dictionary key for every necessary year and tie its with
	#value that's a new DEEPCOPY of twelveMonth. Without deepcopy we get
	#same lists of files in every year 

	for k, v in extLists.items(): 
		if k == 'PNG' or k == 'already sorted': #k is name of extention
				continue
		for item in v: #v is list of files
			mo = dateRegex.search(item)
			if mo != None:
				yearDict[mo.group(1)][mo.group(2)].append(item)
				#add file to corresponding location, 
				#e.g.: year 2016 month january
				logFile.write('\nFile ' + item + ' was added to ' + 
					'yearDict[' + mo.group(1) + '][' + mo.group(2) + ']')
			else:
				mismatchedFiles.append(item)

	monthToPrint = {'01': 'January',
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
	#print out and log list of photos and videos by month and year
	for yearDictKey, yearDictValue in yearDict.items():
		for monthDictKey, monthDictValue in yearDictValue.items():
			if len(monthDictValue) != 0:
				print(str(len(monthDictValue)) + 
					' file was created in ' + monthToPrint[monthDictKey] + 
					' of ' + yearDictKey + '.')
				logFile.write('\n\n' + str(len(monthDictValue)) + 
				' file was created in ' + monthToPrint[monthDictKey] + ' of ' 
				+ yearDictKey + ': \n')
			for file in monthDictValue:
				logFile.write(file + '\n')
			

	if len(mismatchedFiles) > 0:
		prlog('\nThere are ' + str(len(mismatchedFiles)) + 
			' mismatched files.\n' + 
			'They will be copied in folder named "Mismatched".')
		for file in mismatchedFiles:
			logFile.write(file + '\n')
			#message about mismatched files
	
	return mismatchedFiles, yearDict	

###########################copy fils regardless of date ##################

def copyWithoutDate(name, files):
	global wasCopied
	global alreadyExist

	logFile.write('Copy ' + name + ' files...\n\n')
	print('Copy ' + name + ' files...\n')
	
	alreadySorted = syncDB['as'] #get list of already sorted files
	
	if os.path.exists(os.path.join(sortedPhotos, name)):
		prlog('Warning: folder "' + name + 
			'"" in destionation folder already exists')
	else:	
		os.mkdir(os.path.join(sortedPhotos, name))
	i = 0	
	for item in files:
		if os.path.exists(os.path.join(sortedPhotos, name, item)):
			logFile.write('Error: ' + item + 
				' is already in ' + name + '\n')
			alreadySorted.append(item)
			alreadyExist += 1 #count skipped files
			continue
		else:
			shutil.copy2(os.path.join(unsortedPhotos, item), 
				os.path.join(sortedPhotos, name, item)) #copy file
			wasCopied += 1
			if item not in alreadySorted:
				alreadySorted.append(item)
			logFile.write(os.path.join(unsortedPhotos, item) + 
				' copy to ' + os.path.join(sortedPhotos, name, item) + '\n')
			#log which and where to file was copied

	syncDB['as'] = alreadySorted	

#############################  copyEngine  ##############################

def copyEngine(filesByDate):
	prlog('\nStart to copy photo and video by date...')

	global wasCopied
	global alreadyExist

	alreadySorted = syncDB['as'] #get list of already sorted files

	monthToPrint = {'01': '[01] January',
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

	################ copy files by year and month #################

	#### make folder for year if it hasn't existed yet ####
	for yearDictKey, year in filesByDate.items():
		if not os.path.exists(os.path.join(sortedPhotos, yearDictKey)):
			os.mkdir(os.path.join(sortedPhotos, yearDictKey))
			logFile.write(os.path.join(sortedPhotos, yearDictKey) 
				+ ' was created\n')

		#### make folder for month if it hasn't existed yet ###	
		for monthDictKey, month in year.items():
			pathToMonth = os.path.join(sortedPhotos, 
				yearDictKey, monthToPrint[monthDictKey])
			if not os.path.exists(pathToMonth) and len(month) != 0: 
				os.mkdir(pathToMonth)
				print('Now copy to ' + pathToMonth + '...')
				logFile.write(pathToMonth + ' was created\n')
			elif os.path.exists(pathToMonth) and len(month) != 0:
				prlog('\nNow copy to ' + pathToMonth + '...')	
			
			#### copy files by year and month ####
			for file in month:
				oldPathToFile = os.path.join(unsortedPhotos, file)
				newPathToFile = os.path.join(sortedPhotos, yearDictKey, 
					monthToPrint[monthDictKey], file)
				if os.path.exists(newPathToFile):
					prlog('Warning: ' + file + ' already exists.')
					alreadySorted.append(file)
					alreadyExist += 1 #count skipped files
				else:
					shutil.copy2(oldPathToFile, newPathToFile)
					wasCopied += 1
					if file not in alreadySorted:
						alreadySorted.append(file)	
					logFile.write(oldPathToFile + ' copy to ' 
						+ newPathToFile + '\n')

	prlog('\nCopying of files is finished!!')

	syncDB['as'] = alreadySorted		

####################### wasCopied log and print  ######################				
def wasCopiedEngine():

	global wasCopied
	global alreadyExist

	if wasCopied > 0:
		prlog('\n' + str(wasCopied) + ' files were copied')
		if alreadyExist == 1:
			prlog('There is 1 skipped file')
		elif alreadyExist > 1:
			prlog(str(alreadyExist) + ' files were skipped')
		elif alreadyExist == 0:
			prlog('There are no skipped files')
	else:
		prlog('All files (' + str(alreadyExist) + ' from ' 
			+ str(numWithoutAlreadySorted) + 
			') already exist in destination folder')

########################check if folder for work exist#################

if os.path.exists(os.path.join('D:/', 'PythonPhoto', 'sortedPhotos')):
	#mind the syntax: it is 'D:/', neither 'd', nor 'D:', nor "D:/"
	
	logFile = open('D:\\PythonPhoto\\sortedPhotos\\logFile.txt', 'w')
	logFile.write('Program started. Log file was created.\n\n')
	sortedPhotos = ('D:\\PythonPhoto\\sortedPhotos')
	logFile.write('Path to main folders was created\n\n')
else:
	prlog(os.path.join('D:/', 'PythonPhoto', 'sortedPhotos') + 
		' doesn\'t exist')
	sys.exit()

if os.path.exists(os.path.join('D:/', 'PythonPhoto', 'unsortedPhotos')):
	unsortedPhotos = ('D:\\PythonPhoto\\unsortedPhotos')
else:
	prlog(os.path.join('D:/', 'PythonPhoto', 'sortedPhotos') + 
		' doesn\'t exist')
	sys.exit()	

#############################  First menu ###############################

logFile.write('Start to analize for your files? (y/n)\n\n')

while True:
	start = input('\nStart to analize your files? (y/n)\nYour answer is: ')
	if start == 'y':
		logFile.write('Got "y". Call sortByExtEngine()\n\n')
		#checkAlreadySortedFiles()
		numWithoutAlreadySorted, numAlreadySorted, withoutAlreadySorted = checkAlreadySortedFiles(unsortedPhotos)
		
		if numWithoutAlreadySorted > 0:
			###figuring out total size of all unsorted files###
			logFile.write('Call sizes()\n\n')
			logFile.write('Start to figuring out total size of unsorted files\n\n')
			totalSize = sizes(withoutAlreadySorted)
			prlog('\nTotal size of ' + str(numWithoutAlreadySorted) + ' files is ' 
			+ str("%0.2f" % totalSize) + ' MB\n')
			listByExtentions = sortByExtEngine(withoutAlreadySorted)
			mismatchedFiles, filesByDate = sortByDate(listByExtentions)
			listByExtentions['mismatched'] = mismatchedFiles
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

##################### Menu to ask user to start copying ##################

if numWithoutAlreadySorted > 0: #if there is anything to copy 
	while True:
		prlog('\n\n' + str(numWithoutAlreadySorted) + ' files are ready to copy.')
		prlog('Destination is: ' + sortedPhotos)

		start = input('Start? (y/n)\nYour answer is: ')
		logFile.write('Start? (y/n)\nYour answer is: ')
		if start == 'y':
			logFile.write('Got "y".\n\n')
			wasCopied = 0 #global variables to count files in different functions
			alreadyExist = 0

			#### part for copying files regardless of date ####
			numOtherFiles = (len(listByExtentions['PNG']) + 
				len(listByExtentions['other']) + len(listByExtentions['mismatched']))

			#call copyWithoutDateEngine for specific file lists if them isn't empty
			if numOtherFiles > 0:
				for k,v in listByExtentions.items():
					if k == 'JPG' or k == 'video' or len(v) < 1:
						continue
					else:
						logFile.write('\ncopyWithoutDate was invoked\n')
						copyWithoutDate(k,v)

			copyEngine(filesByDate)
			wasCopiedEngine()
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
syncDB = None #workaround for some python bug with closing shelve
logFile.write('\nProgram has reached end. Closing logFile.')
logFile.close()

# ^((?:201[0-9]))-((?:0|1)(?:[0-9]))-((?:[0-3])(?:[0-9])).*$
