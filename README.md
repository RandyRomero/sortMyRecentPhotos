# sortMyRecentPhotos
Small script to sort photo from folder by date and extension.

Written by Aleksandr Mikheev

Python 3

https://github.com/RandyRomero/sortMyRecentPhotos


This as s script for sorting out photos from a folder given by user.
If you have folder with many unsorted photos (and not only photos),
you can run this script in order to:
- Get information how many files there are
- Get total size of all files
- Get total number and size of jpg files, for example:
    - Total number of JPG files is 518.
    - Total size of JPG files is 1641.38 MB.
- Get total number and size of png files
- Get total number and size of video files
- Get total number and size of other files
- Get all your jpg photos sorted out by month and year, for example:
    - 12 file(s) were created in April of 2016.
    - 10 file(s) were created in December of 2016.
    - 34 file(s) were created in October of 2017.
    - 453 file(s) were created in November of 2017.
    - 10 file(s) were created in February of 2009.
    - 6 file(s) were created in April of 2012.
    - 10 file(s) were created in May of 2015.

- Copy your files in a new directory (chosen by you). 
Inside this directory will be folder name by aforementioned types (jpg, png, video, mismatched).
Inside JPG folder will be several folders named by year. Inside every year will be folders with month.
Inside every month will be photos, which have been taken in corresponding year and month.

Firstly script tries to take date from filename. If there is no valid date in filename,
script opens files to read date from EXIF. 

