#!/usr/bin/python
# Filename: acrobat_settings.py
import os


print "SETTING SERIAL AND ARCHIVING PARAMETERS FOR DATA AQUISITION"
print"*************************************************************"


# set up the output settings
###################################
output_settings = {}
# define the cruise 
output_settings['cruise'] = 'LabTest1607'

# define the target folder

_platform = os.name # find the operating system
# pull the computer name based on the operating system
if _platform == 'posix': # MAC OSX
	output_settings['computer_name'] = os.uname()[1]
elif _platform =='nt': # WINDOWS
	output_settings['computer_name'] =  os.environ['COMPUTERNAME']
# define the filepath depending on the computer
if output_settings['computer_name'] =='ZHEMCHUG':
    output_settings['folder']  = 'C:/Users/Public'
elif output_settings['computer_name'] == 'hekla.pmel.noaa.gov':
	output_settings['folder']  = '/Users/martini/UWGoogleDrive/RESEARCH'
elif output_settings['computer_name'] == 'Kims-MacBook-Air.local':
    output_settings['folder']  = '/Users/Martini/UWGoogleDrive/RESEARCH'
else:
    output_settings['folder']  = []



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