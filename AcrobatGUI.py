 #!/usr/bin/python
# filename: testGUI.py

# pull in dependencies
import Tkinter as tk
import ttk as ttk
from threading import Thread, Event
import time, os, datetime, serial, sys
from shutil import copyfile
from serial import SerialException
from memory_profiler import profile

# Change the directory where python finds files according to the computer
_platform = os.name # find the operating system
# pull the computer name based on the operating system
if os.name == 'posix': # MAC OSX
	if os.uname()[1] == 'hekla.pmel.noaa.gov':
		os.chdir('/Users/martini/UWGoogleDrive/GitHub/acrobat')
	else:
		os.chdir( '/Users/Martini/UWGoogleDrive/ipythonnb/acrobat')

# pull in the predetermined instrument settings
from acrobat_settings import *

# trim the payload to instruments with serial port settings that are defined
for k in payload.keys():
	if not 'name' in payload[k]:
		del payload[k]

# preallocate serials and data file dictionaries
serials = {}
datfiles = {}
start_time = []

# DEFINE THE CLASS THAT MAKES THE WINDOW ##############################
class Window(tk.Frame):
	# INITIALIZE THE GUI
	def __init__(self, parent):
		# inherit from tk.Frame
		tk.Frame.__init__(self,parent)
		#reference the parent widget
		self.parent = parent
		# create the GUI with GUIinit
		self.initUI()

	# INITIALIZE THE GUI 
	def initUI(self):
		# create and place the window
		self.createWindow()
		self.placeWindow()

		# make graphical frames to contain the entry fields
		folderFrame = self.makeEntryField(self, 'ROOT FOLDER', output_settings['folder'])
		cruiseFrame = self.makeEntryField(self, 'CRUISE', output_settings['cruise'])

		# MAKE THE CONTROL BUTTONS 
		# make a start button
		startButton = tk.Button(self, text='START', command = self.startDataAcq, activebackground='#66ffcc', width = 20)
		startButton.pack(side = tk.LEFT, padx=25, pady=5,  ipady=5)
		# make a stop button 
		stopButton = tk.Button(self, text='STOP', command = self.stopDataAcq, activebackground= 'red', width = 20)
		stopButton.pack(side = tk.LEFT, padx=25, pady=5, ipady=5)
		# make a quit button
		quitButton = tk.Button(self, text='QUIT', command=self.quitDataAcq, activebackground='#3399ff', width = 20)
		quitButton.pack(side=tk.LEFT, padx=25, pady=5, ipady=5)

		# CREATE THE CONTROLLER FOR THE MULTIPLE THREADS 
		global control
		control = Controller()

	# FUNCTIONS TO CREATE THE MAIN GUI WINDOW ##############################
	def createWindow(self):
		""" create the main GUI window"""
		# give the window a title
		self.parent.title( 'Acrobat Data Acquisition')
		# set the style
		self.style = ttk.Style()
		self.style.theme_use('default')
		self.pack(fill= tk.BOTH, expand=1)
			
	def placeWindow(self):
		"""define the window location"""
		# window size
		w = 600
		h = 300
		# find the screen size
		sw = self.parent.winfo_screenwidth()
		sh = self.parent.winfo_screenheight()
		# now define the location on the current screen
		x = (sw/2-0.5*w)
		y = (sh/2-0.5*h)
		self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

	class makeEntryField(tk.Frame):
		""" Class to create a standardized text entry """
		def __init__(self, parent, labelin, entryin):
			# inherit from tk.Frame
			tk.Frame.__init__(self, parent)
			#reference the parent widget
			self.parent = parent
			# define the entries
			self.labelstr = labelin
			self.defaultentry = entryin
			self.entrystr = self.defaultentry
			# define the variable
			entrystr = tk.StringVar()
			# add a frame for the cruise info
			self.frame = tk.Frame(parent, relief=tk.RAISED)
			self.frame.pack(fill=tk.X, pady = 5) 
			# def makeLabel(self):
			self.label = tk.Label(self.frame, text=self.labelstr+':')
			self.label.pack(side=tk.LEFT, anchor = tk.N)
			# make the entry
			self.entry = tk.Entry(self.frame, textvariable = entrystr)
			self.entry.pack(side=tk.LEFT, fill = tk.X)
			self.entry.insert(0, self.defaultentry)
			# add a button
			# self.button = tk.Button(self.frame, text='UPDATE', command = self.updateButton)
			# self.button.pack(side = tk.RIGHT, padx = 5)

		def updateButton(self):
			# pull the entry 
			newentry = self.entrystr.get()
			print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
			print "Changing "+self.labelstr
			print 'from : '+self.defaultentry
			print 'to : '+newentry
			print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
			# change the entry
			# self
			# confirm_dir(folderstr, cruise)
			return newentry

	# FUNCTIONS TO CONTROL DATA ACQUSITION CONTROL 	##############################
	def startDataAcq(self):
		"""Initialize the data acquisiton"""
		global payload, control, output_settings, serials, datfiles
		# INITIALIZE THE OUTPUT FOLDER STRUCTURE
		check_dir(output_settings['folder'], output_settings['cruise'], payload)
		confirm_dir(output_settings['folder'], output_settings['cruise'])
		# FIND THE START TIME
		output_settings['start_time'] = init_time()
		# PRINT THE START TIME
		print_spacer()
		print 'Local Time: ', time.ctime(output_settings['start_time'])
		print 'UTC: ', time.asctime(time.gmtime(output_settings['start_time']))
		
		# LOOP THROUGH THE SCIENTIFIC PAYLOAD
		for k in payload.keys():
			try:
				if serials[k].isOpen():
					close_serial(serials[k])
			except KeyError:
				print ' '
				# print 'Serial port connected to '+k+' was not previously open.'
			# open the serial port
			serials[k] = init_serial(payload[k])
			if serials[k].isOpen():				
				# print the serial info
				print 'Receiving data from '+k
				# initialize the data file
				datfiles[k] = init_datafile(output_settings, payload[k])
				# read one line because the first one after opening a port is usually gibberish
				line = serials[k].readline()
			else: 
				print 'Unable to connect to serial port '+payload[k]['port']+' connected to '+k
			# pause get everything setup
			time.sleep(1)
		# start the loop 
		control.combine()

	def stopDataAcq(self):
		global control, payload, keys, serials
		print_spacer()
		print 'STOPPING DATA ACQUISITION'
		control.stop()
		for k in payload.keys():
			if serials[k].isOpen():
				# close the serial port
				close_serial(serials[k])
				# close the datafile
				close_datafile(datfiles[k])
			else:
				print k+' serial and data file never opened'
		# copy all the acrobat flying files to the flight software			
		copy_acrobat_logs(output_settings)

	def quitDataAcq(self):
		"""close all processes and the window"""
		# stop the data acquition if threads still running
		global control, payload, keys, serials, output_settings
		if not control.stop_threads.is_set():
			print_spacer()
			print 'STOPPING DATA ACQUISITION'
			control.stop()
			for k in serials.keys():
				if serials[k].isOpen():
					# close the serial port
					close_serial(serials[k])
					# close the datafile
					close_datafile(datfiles[k])
				else:
					print k+' serial and data file never opened'
		# copy all the acrobat flying files to the flight software			
		copy_acrobat_logs(output_settings)
		# close all the windows
		time.sleep(1)
		self.parent.destroy()
		

# CONTROLLER CLASS FOR DATA ACQUSITION THREADS ##############################
class Controller(object):
	def __init__(self):
		# define all the threads and threadnames
		global payload
		self.threadnames = []
		self.threads = []
		print_spacer()
		for k in payload.keys():
			print 'Loading serial port settings for '+payload[k]['name']+' in '+k+'...'
			self.threadnames.append(k)
			self.threads.append(None)
		# define an event to stop the threads
		self.stop_threads = Event()

	def loop(self, k):
		global serials, datfiles, datalog_settings
		# define the time when data log starts
		start_dat = output_settings['start_time']
		while not self.stop_threads.is_set():
			# parse the incoming lines from the serial connection
			parse_serialline(serials[k], datfiles[k])
			# decide whether to initiate a new data file
			if time.time()<start_dat+datalog_settings['file_length']:
				continue
			else:
				serials[k].reset_input_buffer()
				serials[k].reset_output_buffer()
				# close the data file
				close_datafile(datfiles[k])
				datfiles[k] = None
				# open a new datafile
				datfiles[k] = init_datafile(output_settings, payload[k])
				start_dat = init_time()

	def combine(self):
		global serials
		# clear the command to stop
		self.stop_threads.clear()
		for i in range(0, len(control.threads)): # cycle through potential instrument threads
			if serials[self.threadnames[i]].isOpen(): # only start thread if corresponding serial port is open
				# start threads
				self.threads[i] = Thread(target = self.loop, args = (self.threadnames[i],))
				self.threads[i].start()
				# print status
				print_spacer()
				print 'Starting thread '+str(i)+'...'
				print 'Acquiring data from '+self.threadnames[i]+'...'

	def stop(self):
		self.stop_threads.set()
		for i in range(0, len(control.threads)):
			print_spacer()
			try:
				print 'Closing thread '+str(i)+'.'
				print 'Stopping data acquisition from '+self.threadnames[i]+'.'
				self.threads[i].join()
			except AttributeError:
				print 'Already closed thread '+str(i)+'.'
				print 'Data not acquired from '+self.threadnames[i]+'.'
			self.threads[i] = None

# DATA ACQUISITION FUNCTIONS ################################			
# see above

# DATA ACQUISITON INITIALIZATION FUNCTIONS ##############################
def check_dir(folderstr, cruise, payload):
	"""check if the cruise directory exists"""
	print_spacer()
	if os.path.exists(folderstr+'/'+cruise):
		print 'File structure for cruise '+cruise+' already exists.'
	else:
		print 'Create new file directory for '+cruise+'.'
		os.makedirs(folderstr+'/'+cruise+'/DATA/ACROBAT/RAW')
		os.makedirs(folderstr+'/'+cruise+'/DATA/ACROBAT/PROCESSED')
	# check to make sure all instruments in the payload have a folder
	for k in payload.keys():
		if os.path.exists(folderstr+'/'+cruise+'/DATA/ACROBAT/RAW/'+payload[k]['name']) == False:
			dirname = folderstr+'/'+cruise+'/DATA/ACROBAT/RAW/'+payload[k]['name']
			os.makedirs(dirname)
			print 'Creating '+dirname+'...'
	# add a folder for the flight software
	if os.path.exists(folderstr+'/'+cruise+'/DATA/ACROBAT/RAW/ACROBAT') == False:
			dirname = folderstr+'/'+cruise+'/DATA/ACROBAT/RAW/ACROBAT'
			os.makedirs(dirname)
			print 'Creating '+dirname+'...'

def confirm_dir(folderstr, cruise):
	"""print a confirmation of the folder """
	print_spacer()
	print 'Data will be output to '+folderstr+'/'+cruise+"/DATA/ACROBAT/RAW"

def init_time():
	""" define the time the script starts running """
	starttime = time.time()
	return starttime # return the start time


# data files ###################################
def init_datafile(output_settings, instrument):
    """ initialize and open the data file """
    # find the current directory
    target_dir = '/'.join([output_settings['folder'], output_settings['cruise'], 'Data/Acrobat/RAW',instrument['name']])
    print_spacer()
    
    # make a new file
    print 'Creating new file....'
    # find the current time and write as string
    current_time = time.strftime("%Y-%m-%dT%H%MZ", time.gmtime(time.time()))
    # give it a name
    filestr = current_time+'_'+output_settings['cruise']+instrument['name']+'RAW.dat' # concatenates strings using 
    # print target_dir+'/'+filestr
    # now set the target 
    targetstr = '/'.join([target_dir,filestr]) # concatencates strings using join
    print targetstr
    # open the text file
    fs = open(targetstr, 'w')
    return fs # return the file id

def close_datafile(fs):
    """close the text file"""
    fs.close() # fs is the output from init_datafile

def copy_acrobat_logs(output_settings):
	"""copy the acrobat flight files into the cruise folder"""
	source_dir = '/'.join([output_settings['folder'], 'SeaSciences/data'])
	target_dir = '/'.join([output_settings['folder'], output_settings['cruise'], 'DATA/ACROBAT/RAW/ACROBAT'])
	print_spacer()
	print 'Copying files from '+source_dir
	print 'to '+target_dir 
	time.sleep(1)
	# find when the target dir was created 
	target_time = os.stat(target_dir).st_ctime
	# pull the files from the source director
	files =  os.listdir(source_dir)
	# find all the .dat files
	files = filter(lambda x: x[-4:]=='.dat', files)
	for f in files:
		copyfile( '/'.join([source_dir, f] ), '/'.join([target_dir, f]))
		

# serial ports ###################################
def init_serial(instrument):
	""" initialize a serial connection """
	# open a serial port
	try:
		ser = serial.Serial(instrument['port']) # try and open th serial port
	except:
		ser = serial.Serial() # make an empty serial port object if not
	# display serial  port status
	print_spacer()
	if ser.isOpen()==True:
	    print 'Serial port '+instrument['port']+ ' has been opened.'
	else:
	    print 'Serial port '+instrument['port']+' failed to open.'		# set up the parameters
	# set up the serial port parameters
	ser.baudrate = instrument['baudrate'] # set the baudrate
	ser.bytesize = instrument['bytesize'] # 
	ser.parity = instrument['parity'] # 
	ser.stopbits = instrument['stopbits'] # 
	ser.timeout = instrument['timeout'] # specify a timeout (in seconds) so the port doesn't hang
	ser.xonxoff = instrument['xonxoff'] # 
	ser.rtscts = instrument['rtscts'] # 
	ser.dsrdtr = instrument['dsrdtr'] # 
	#return the serial port back to the caller
	return ser 

def close_serial(ser):
	"""close the serial port"""
	ser.close()
	if ser.isOpen():
	    print ser.portstr+' could not be closed and is still open.'
	else:
	    print 'Serial Port '+ser.portstr+' has been closed.'  
	return ser

# acquire data ###################################
def parse_serialline(ser, fs):
    """Read the a serial data stream and write to a file"""
    #read a line
    line = ser.readline()
    # if string from instrument is empty, flush the serial input
    # if not line:
    # 	ser.reset_input_buffer()
    # 	print 'resetting buffers on '+ser.portstr
    # make a time stamp
    # timestamp = datetime.datetime.utcnow().isoformat() # get the  in iso8601 format
    # concat the timestamp and line out to make an output string
    strout = datetime.datetime.utcnow().isoformat()+','+line.strip()+'\n'
    print strout
    # write to file (remove last character so there is no extra carriage return and line feed)
    fs.write(strout)

def print_spacer():
	print ' '
	print '------------------------'

# WRAPPER FUNCTION THAT EXECUTES EVERYTHING ##############################
def main():
	root = tk.Tk()
	app = Window(root)
	root.mainloop()

if __name__=='__main__':
	main()				





