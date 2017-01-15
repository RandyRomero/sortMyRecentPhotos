#!python3 

import os, shutil, sys


logFile = open('D:\\PythonPhoto\\sortedPhoto\\logFile.txt', w)
logFile.write('Program started. Log file created\n')


unsortedPhotos = ('D:\\PythonPhoto\\unsortedPhoto')
sortedPhotos = ('D:\\PythonPhoto\\sortedPhoto')
logFile.write('Path to main folders created\n')

start = input('\nStart to look for your photos? (y/n)')
logFile.write('Start to look for your photos? (y/n)\n')


while True:
	if start == 'y':
		logFile.write('Got "y".\n')
		#start sort engine
		break
	elif start == 'n':
		logFile.write('Got "n". Exit script.\n')
		print('Goodbye')
		sys.exit()
	else:
		logFile.write('Got wrong input. Ask again...\n')
		print('Input error. You should type in y or n')	
		continue
		


