
import os, shelve

def checkAlreadySortedFiles(unsortedPhotos):
		if os.path.exists(os.path.join(unsortedPhotos, '_sync')):
			print(os.path.join(unsortedPhotos, '_sync') + ' exists.')
			syncDB = shelve.open(os.path.join(unsortedPhotos, '_sync', 'filesyncDB'))

			try:
				alreadySorted = syncDB['as']
			except KeyError:
				print('Database doesn\'t have list of files')
				alreadySorted = []
				syncDB['as'] = alreadySorted
			#extract list of file nsmes from shelve
		else:
			print(os.path.join(unsortedPhotos, '_sync') + ' doesn\'t exists')
			os.mkdir(os.path.join(unsortedPhotos, '_sync'))
			syncDB = shelve.open(os.path.join(unsortedPhotos, '_sync', 'filesyncDB'))
			alreadySorted = []
			syncDB['as'] = alreadySorted
			print('List of files has been already in the DB') 

		return syncDB


if os.path.exists(os.path.join('D:/', 'PythonPhoto', 'unsortedPhotos')):
	unsortedPhotos = ('D:\\PythonPhoto\\unsortedPhotos')
	syncDB = checkAlreadySortedFiles(unsortedPhotos)
else:
	print(os.path.join('D:', 'PythonPhoto', 'sortedPhotos') + ' doesn\'t exist')


syncDB.close()