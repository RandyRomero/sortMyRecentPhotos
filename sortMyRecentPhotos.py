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

def sortEngine():
	logFile.write('Getting list with names of files in ' + unsortedPhotos + 
		'\n\n')
	files = os.listdir(unsortedPhotos)

	logFile.write('Print that in ' + unsortedPhotos + ' are ' 
		+ str(len(files)) + ' files\n\n')
	print('Here are ' + str(len(files)) + ' unsorted files.')
	
	logFile.write('Call sizes()\n\n')
	sizes(files)


	jpgList = [] 
	pngList = []
	videoList = []
	otherList = []
	
	logFile.write('Start to count PNG files...\n')
	for item in os.listdir(unsortedPhotos):
		if item.endswith('.PNG') or item.endswith('.png'):
			pngList.append(item)
		elif item.endswith('.JPG') or item.endswith('.jpg') or item.endswith('.JPEG'):
			jpgList.append(item)
		elif item.endswith('.MP4') or item.endswith('.3GP'):
			videoList.append(item)
		else:
			otherList.append(item)
			print(item)


	logFile.write('\nThe total amount of JPG files is ' + str(len(jpgList)) + '\n')	
	print('\nThe total amount of JPG files is ' + str(len(jpgList)) + '\n')
	logFile.write('\nThe total amount of PNG files is ' + str(len(pngList)) + '\n')	
	print('\nThe total amount of PNG files is ' + str(len(pngList)) + '\n')
	logFile.write('\nThe total amount of video files is ' + str(len(videoList)) + '\n')	
	print('\nThe total amount of video files is ' + str(len(videoList)) + '\n')
	logFile.write('\nThe total amount of other files is ' + str(len(otherList)) + '\n')	
	print('\nThe total amount of other files is ' + str(len(otherList)) + '\n')

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


