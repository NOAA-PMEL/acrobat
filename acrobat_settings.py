#!/usr/bin/python
# Filename: acrobat_settings.py
import os


print "SETTING SERIAL AND ARCHIVING PARAMETERS FOR DATA AQUISITION"
print"*************************************************************"

# define the cruise #################################
cruise = 'LabTest1607'

# define the target folder depending on the computer ###################################
# find the operating system
_platform = os.name
# pull the computer name based on the operating system
if _platform == 'posix': 
	# MAC OSX
	computer_name = os.uname()[1]
elif _platform =='nt':
	#windows 
	computer_name = os.environ['COMPUTERNAME']
# define the filepath and instrument input parameters depending on the computer
if computer_name=='ZHEMCHUG':
    folderstr  = 'C:/Users/Public'
elif computer_name == 'hekla.pmel.noaa.gov':
	folderstr = '/Users/martini/UWGoogleDrive/RESEARCH'
else:
    folderstr  = 'NONE_YET'


# serial port settings for instruments ###################################
payload = {}
# define the parameters for Pie A: Wetlabs Triplet 
payload['pieA'] = {'name':'Triplet', 'port':'COM5', 'baudrate':19200, 'bytesize':8, 'parity':'N',
         'stopbits':1, 'timeout':1, 'xonxoff':0, 'rtscts':0, 'dsrdtr':0}
# define the parameters for Pie B: EMPTY
payload['pieB'] = {}
# define the parameters for Pie C: SeaBird 49 FastCAT CTD
payload['pieC'] = {'name':'FastCAT', 'port':'COM7', 'baudrate':9600, 'bytesize':8, 'parity':'N',
         'stopbits':1, 'timeout':1, 'xonxoff':0, 'rtscts':0, 'dsrdtr':0}
# define the parameters for Pie D: EMPTY
payload['pieD'] = {}
# define the parameters for Pie E: SUNA Nitrate Sensor
payload['pieE'] = {'name':'SUNA', 'port':'COM9', 'baudrate':57600, 'bytesize':8, 'parity':'N',
         'stopbits':1, 'timeout':1, 'xonxoff':0, 'rtscts':0, 'dsrdtr':0}

# define the GPS parameters
payload['GPS'] = {'name':'GPS', 'port':'COM13', 'baudrate':4800, 'bytesize':8, 'parity':'N',
         'stopbits':1, 'timeout':1, 'xonxoff':0, 'rtscts':0, 'dsrdtr':0}


# settings for data logging ###################################
datalog_settings = {}

# time in seconds between new data files
datalog_settings['file_length'] = 10*60 # 1 min!