import re, collections

############first we need to know home many years we have ################

yearList = [] #

logFile.write('Compile regex for dates in files...\n\n')
dateRegex = re.compile(r''' 
	^((?:201[0-9]))- 		#year - Group 1
	((?:0|1)(?:\d))-		#month - Group 2
	((?:[0-3])(?:\d))		#day - Group 3
	.*$ 					#all other symbols after
	
	''', 
	re.VERBOSE)

for k, v in extLists.items(): 

	if k == 'PNG': #k is name of extention
			continue
		
	for item in v: #v is list of files
		mo = dateRegex.search(item)
		yearNum = mo.group(1)
		if yearNum not in yearList:
			yearList.append(yearNum)

yearDict = collections.OrderedDict([])

january, february, march, april = ([] for i in range(4))
may, june, july, august = ([] for i in range(4))
september, october, november, december = ([] for i in range(4))
#declare 12 lists fo each month

twelveMonth = collections.OrderedDict([])
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

mismatchFiles = []

for year in yearList: 
	yearDict[year] = twelveMonth
#add year with tvelwe month in dictionary

for k, v in extLists.items(): 
	for item in v: #v is list of files
		mo = dateRegex.search(item)
		if mo != None:
			yearDict[mo.group(1)][mo.group(2)].append(mo.group())
		else:
			mismatchFiles.append()


logFile.write('\nHere is list of unsorted files.' +
	 'They won\'t be copied anywhere:\n')
print('\nHere is list of unsorted files. They won\'t be copied anywhere:')
for file in mismatchFiles:
	print(file)
	logFile.write(file + '\n')
	#message about mismatch files

for yearInDictNum, monthDict in yearDict.items():
	for monthInDictNum, month in monthDict.items():
		print('List of photo that was taken in ' + monthInDict + 
			' of ' + yearInDictNum + ': \n')	
		#print list of photo by month and year