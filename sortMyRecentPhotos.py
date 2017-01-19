#!python3 

import os, shutil, sys


logFile = open('D:\\PythonPhoto\\sortedPhotos\\logFile.txt', 'w')
logFile.write('Program started. Log file created\n\n')


unsortedPhotos = ('D:\\PythonPhoto\\unsortedPhotos')
sortedPhotos = ('D:\\PythonPhoto\\sortedPhotos')
logFile.write('Path to main folders created\n\n')

def sizes(files):
	logFile.write('Start to figuring out total size of unsorted files\n\n')

	totalSize = 0
	for file in files:
		size = os.path.getsize(os.path.join(unsortedPhotos, file))
		totalSize += size
	totalSize = totalSize / 1024 / 1024

	logFile.write('Total size of ' + str(len(files)) + ' files is ' 
		+ str("%0.2f" % totalSize) + ' MB\n\n')
	print('Total size of ' + str(len(files)) + ' files is ' 
		+ str("%0.2f" % totalSize) + ' MB\n')
	#TODO truncate digits after comma

def sortEngine():
	logFile.write('Getting list with names of files in ' + unsortedPhotos + 
		'\n\n')
	files = os.listdir(unsortedPhotos)

	logFile.write('Print that in ' + unsortedPhotos + ' are ' 
		+ str(len(files)) + ' files\n\n')
	print('Here are ' + str(len(files)) + ' unsorted files.')
	
	logFile.write('Call sizes()\n\n')
	sizes(files)

	png = 0
	jpg = 0
	other = 0
	logFile.write('Start to count PNG files...\n')
	for item in os.listdir(unsortedPhotos):
		if item.endswith('.PNG') or item.endswith('.png'):
			logFile.write(str(item) + '\n')
			png += 1
		elif item.endswith('.JPG') or item.endswith('.jpg') or item.endswith('.JPEG'):
			logFile.write(item + '\n')
			jpg += 1
		else:
			other += 1
			print(item)


	logFile.write('\nThe total amount of JPG files is ' + str(jpg) + '\n')	
	print('\nThe total amount of JPG files is ' + str(jpg) + '\n')
	logFile.write('\nThe total amount of PNG files is ' + str(png) + '\n')	
	print('\nThe total amount of PNG files is ' + str(png) + '\n')
	logFile.write('\nThe total amount of other files is ' + str(other) + '\n')	
	print('\nThe total amount of other files is ' + str(other) + '\n')

start = input('\nStart to look for your photos? (y/n) Your answer is: ')
logFile.write('Start to look for your photos? (y/n)\n\n')

while True:
	if start == 'y':
		logFile.write('Got "y". Call sortEngine()\n\n')
		sortEngine()
		break
	elif start == 'n':
		logFile.write('Got "n". Exit script.\n\n')
		print('Goodbye')
		sys.exit()
	else:
		logFile.write('Got wrong input. Ask again...\n\n')
		print('Input error. You should type in y or n')	
		continue

logFile.write('Program has reached end. Closing logFile.')
logFile.close()		


