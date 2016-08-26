#!/usr/bin/python
# Filename: acrobat.py

# Import the appropriate modules #################################
import time, datetime, serial, os, threading
import Tkinter as tk

# pull in the predetermined instrument settings
from acrobat_settings import *


# initial settings ###################################
# def init_time():
#     """ define the time the script starts running """
#     starttime = time.time()
#     return starttime # return the start time

# def check_dir(folderstr, cruise, payload):
#  	"""check if the cruise directory exists"""
#  	if os.path.exists(folderstr+'/'+cruise):
#  		print 'File structure for cruise '+cruise+' already exists.'
#  	else:
#  		print 'Create new file directory for '+cruise+'.'
#  		os.makedirs(folderstr+'/'+cruise+'/DATA/ACROBAT/RAW')
#  		os.makedirs(folderstr+'/'+cruise+'/DATA/ACROBAT/PROCESSED')
#  		for k in payload.keys():
#  			if "name" in payload[k]:
#  				os.makedirs(folderstr+'/'+cruise+'/DATA/ACROBAT/RAW/'+payload[k]['name'])
 		

# def confirm_dir(folderstr, cruise):
# 	"""print a confirmation of the folder """
# 	print 'Data will be output to '+folderstr+'/'+cruise+"/DATA/ACROBAT/RAW"

# serial ports ###################################
def init_serial(instrument):
    """ initialize a serial connection """
    # open a serial port
    ser = serial.Serial(instrument['port'])
    if ser.isOpen()==True:
        print ser.portstr+ ' has been opened.'
    else:
        print ser.portstr+ ' failed to open.'

    # set up the parameters
    ser.baudrate = instrument['baudrate'] # set the baudrate
    ser.bytesize = instrument['bytesize'] # 
    ser.parity = instrument['parity'] # 
    ser.stopbits = instrument['stopbits'] # 
    ser.timeout = instrument['timeout'] # specify a timeout (in seconds) so the port doesn't hang
    ser.xonxoff = instrument['xonxoff'] # 
    ser.rtscts = instrument['rtscts'] # 
    ser.dsrdtr = instrument['dsrdtr'] # 
    
    #return the serial port class
    return ser # return the serial port back to the caller

def close_serial(ser):
    """close the serial port"""
    ser.close()
    if ser.isOpen():
        print ser.portstr+' could not be closed and is still open.'
    else:
        print ser.portstr+' is closed.'  
    return ser

# def check_serial(ser):

# data files ###################################
# def init_datafile(folderstr, cruise, inst):
#     """ initialize and open the data file """
#     inst_name = inst['name']
#     # find the current directory
#     target_dir = '/'.join([folderstr, cruise, 'Data/Acrobat/RAW',inst_name])
#     print target_dir
#     # get all the files in the directory
#     files = os.listdir(target_dir)
#     # keep only the dat files
#     files = filter(lambda x: x[-4:]=='.dat', files)
    
#     # check if there are any .dat files
#     if len(files)==0:
#         make_new_datafile = 1
#     else:
#         # sort the files by date
#         files.sort(key = lambda x: os.stat(target_dir+'/'+x).st_mtime)
#         # pull the latest .dat file
#         latest_dat_file = files[-1]
#         print 'Latest .dat file: '+latest_dat_file
#         # if files more than an hour old
#         if time.time()-os.stat(target_dir+'/'+latest_dat_file).st_ctime >datalog_settings['file_length']:
#             make_new_datafile = 1
#         else:
#             make_new_datafile = 0
        
#     if make_new_datafile == 1:
#         # make a new file
#         print 'Last file created more than an hour ago, creating new file....'
#         # find the current time and write as string
#         current_time = time.strftime("%Y_%m_%d_%H%M", time.gmtime(time.time()))
#         # give it a name
#         filestr = current_time+cruise+inst['name']+'RAW.dat' # concatenates strings using 
#         print 'Creating '+filestr
#         #define write to the new file
#         write_mode = 'w'
#     elif make_new_datafile == 0:
#         # Open file made within the last hour
#         filestr = latest_dat_file
#         print 'Opening and appending '+latest_dat_file
#         # define appending the old file
#         write_mode = 'a'

#     # now set the target 
#     targetstr = '/'.join([folderstr,cruise,'Data/Acrobat/RAW',inst_name,filestr]) # concatencates strings using join

#     # open the text file
#     fs = open(targetstr, write_mode)

#     return fs # return the file id

def close_datafile(fs):
    """close the text file"""
    fs.close()
    print fs.name+' is closed'


# Data Acquisition functions ############################################
def run_data_acquisition(folderstr, cruise, serial_in, datalog_settings):
	"""Open serial ports, start data acquisitio and logging"""
	# print the stop instructions
	print_stop_instructions
	# open the serial port and start aquiring data
	fs, serINST, start_time = init_data_acquisition(serial_in)
	time.sleep(1)
	# collect data unitl interrupted manually
	try:
		# define the start time
		start_dat = start_time
		while True:
			parse_serialdata(serINST, fs)
			if time.time()<start_dat+datalog_settings['file_length']:
				continue
			else:
				fs = init_datafile( folderstr, cruise, serial_in)
				start_dat = init_time()

	except KeyboardInterrupt:
		print 'interrupted!'
		#close the data file
		close_datafile(fs)
		# close the serial port
		close_serial(serINST)


def print_stop_instructions():
	"""Print out instructions to stop logging"""
	print "*****************************************************************************"
	print "To stop data collection select INTERRUPT from the KERNAL pull down menu above"
	print "*****************************************************************************"

def parse_serialdata(ser, fs):
    """Read the a serial data stream and write to a file"""
    #read a line
    line = ser.readline()
    # make a time stamp
    timestamp = datetime.datetime.utcnow().isoformat() # get the  in iso8601 format
    # concat to make an output string
    strout = timestamp+','+line
    # print string for now
    print strout
    # write to file (remove last character so there is no extra carriage return and line feed)
    fs.write(strout[:-1])

# def init_data_acquisition(ser):
# 	"""Initialize data aquisition from serial port"""
# 	# find the start timeS
# 	start_time = init_time()
# 	# print it out 
# 	print 'Local Time: ', time.ctime(start_time)
# 	print 'UTC: ', time.asctime(time.gmtime(start_time))
# 	print '--------------------------'

# 	global serINST
# 	# check to see if a serial port is already open
# 	if 'serINST' in globals():
# 		if serINST.isOpen():
# 			# close the serial port
# 			close_serial(serINST)
# 	# now open the correct serial port
# 	serINST = init_serial( ser )
# 	# print the serial port info
# 	print serINST
# 	print '--------------------------'
# 	# open the data file
# 	fs = init_datafile(folderstr, cruise, ser)
# 	# read one line because the first one after opening a port is usually gibberish
# 	line = serINST.readline()
# 	return fs, serINST, start_time


# GPS functions ############################################
def parse_GPSdata(ser, fs):
    """Read the GPS data stream and write to a file"""
    #read a line
    line = ser.readline()
    # only use $GPGGA lines
    if line.find( 'GPGGA') ==1 or line.find('GPZDA')==1:
        # make a time stamp
        timestamp = datetime.datetime.utcnow().isoformat() # get the  in iso8601 format
        # concat to make an output string
        strout = timestamp+','+line
        # print string for now
        # print strout
        # write to file (remove last character so there is no extra carriage return and line feed)
        fs.write(strout[:-1])

  # realtime data display ############################################      


# def init_scrolling_window():
# 	""" create a window to display scrolling window"""
# 	# make the window
# 	root = tk.Tk()
# 	#define the string
# 	str_var = tk.StringVar()
# 	labl = tk.Label(root, textvariable = str_var, height = 10)

# 	root.mainloop()
# 	return root, str_var, labl

# def print_scrolling_line(root, str_var, labl, linein):
# 	""" Print scrolling line in window"""
# 	str_var.set(linein)
# 	labl.pack()
# 	root.mainloop()




