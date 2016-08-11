 #!/usr/bin/python
# filename: testGUI.py

# pull in dependencies
# from acrobat import *
import Tkinter as tk
import ttk as ttk
from threading import Thread, Event
import time, os, datetime, serial, os
from serial import SerialException

# Change the directory where python finds files
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
fs = {}
start_time = []

# define the class that makes the window
class Window(tk.Frame):

	def __init__(self, parent):
		# inherit from tk.Frame
		tk.Frame.__init__(self,parent)
		#reference the parent widget
		self.parent = parent
		# create the GUI with GUIinit
		self.initUI()

	# INITIALIZE THE GUI
	##############################
	def initUI(self):
		# CREATE AND PLACE THE WINDOW
		##############################
		self.createWindow()
		self.placeWindow()

		# MAKE ENTRY FIELDS FOR WHERE DATA IS WRITTEN
		##############################
		# make an entry field for the folder
		folderFrame = self.makeEntryField(self, 'ROOT FOLDER', output_settings['folder'])
		# make an entry field for the cruise
		cruiseFrame = self.makeEntryField(self, 'CRUISE', output_settings['cruise'])
		#*****************************
		# MOAR FRAMES BELOW
		#*****************************

		# MAKE THE CONTROL BUTTONS
		#*****************************
		# make a start button
		startButton = tk.Button(self, text='START', command = self.startDataAcq)
		startButton.pack(side = tk.LEFT, padx=25, pady=5, ipadx = 5, ipady=5)
		# make a stop button 
		stopButton = tk.Button(self, text='STOP', command = self.stopDataAcq)
		stopButton.pack(side = tk.LEFT, padx=25, pady=5, ipadx = 5, ipady=5)
		# make a quit button
		quitButton = tk.Button(self, text='QUIT', command=self.quitDataAcq)
		quitButton.pack(side=tk.LEFT, padx=25, pady=5, ipadx = 5, ipady=5)

		# CREATE THE CONTROLLER FOR THE MULTIPLE THREADS
		#*****************************
		global control
		control = Controller()

	# FUNCTIONS TO CREATE THE MAIN GUI WINDOW
	##############################
	def createWindow(self):
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
		x = (sw-2*w)
		y = (sh-2*h)
		self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))


	# CLASS TO MAKE A STANDARD ENTRY FIELD
	##############################
	class makeEntryField(tk.Frame):
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
			self.button = tk.Button(self.frame, text='UPDATE', command = self.updateButton)
			self.button.pack(side = tk.RIGHT, padx = 5)

		def updateButton(self):
			# pull the entry 
			newentry = self.entrystr.get()
			print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
			print "Changing "+self.labelstr
			print 'from : '+self.defaultentry
			print 'to : '+newentry
			print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
			# change the entry
			self
			# confirm_dir(folderstr, cruise)
			return newentry

	# DATA ACQUSITION CONTROL 	##############################
	def startDataAcq(self):
		"""Initialize the data acquisiton"""
		global payload, control, output_settings, serials, fs
		# INITIALIZE THE OUTPUT FOLDER STRUCTURE
		check_dir(output_settings['folder'], output_settings['cruise'], payload)
		confirm_dir(output_settings['folder'], output_settings['cruise'])
		## run_data_acquisition(folderstr, cruise, serial_in, datalog_settings) ##
		# print a start code
		print_stop_instructions()
		## 	fs, serINST, start_time = init_data_acquisition(serial_in) ##
		# FIND THE START TIME
		start_time = init_time()
		# print it out 
		print 'Local Time: ', time.ctime(start_time)
		print 'UTC: ', time.asctime(time.gmtime(start_time))
		print '--------------------------'
		# LOOP THROUGH THE SCIENTIFIC PAYLOAD
		for k in payload.keys():
			try:
				if serials[k].isOpen():
					close_serial(serials[k])
			except KeyError:
				print 'serial port connected to '+k+' is not open'
			# open the serial port
			try: 
				# open the port
				serials[k] = init_serial(payload[k])
				# print the serial info
				print 'Serial port ', serials[k].port, ' is open'
				print 'Receiving data from '+k
				# initialize the data file
				fs[k] = init_datafile(output_settings, payload[k])
				# read one line because the first one after opening a port is usually gibberish
				line = serials[k].readline()
			except SerialException:
				print 'Unable to connect to serial port '+payload[k]['port']+' connected to '+k
			# spacer
			print '----------------------' # spacer
			# pause get everything setup
			time.sleep(1)
		print serials

		# start the loop 
		control.combine()

	def stopDataAcq(self):
		global control, payload, keys, serials
		control.stop()
		print 'STOPPING DATA ACQUITION'
		print '----------------------'
		for k in payload.keys():
			if k in serials:
				print k
				# close the serial port
				close_serial(serials[k])
				# close the datafile
				close_datafile(fs[k])
			else:
				print 'nothing to close for '+k


	def quitDataAcq(self):
		"""close all processes and the window"""
		# stop the data acquition if threads still running
		global control
		if not control.stop_threads.is_set():
			control.stop()
		# close all the windows
		self.parent.destroy()
		

# CONTROLLER CLASS FOR DATA ACQUSITION THREADS ##############################
class Controller(object):
	def __init__(self):
		# define all the threads and threadnames
		global payload
		self.threadnames = []
		self.threads = []
		for k in payload.keys():
			print 'initializing '+k+'...'
			self.threadnames.append(k)
			self.threads.append(None)
		# define an event to stop the threads
		self.stop_threads = Event()

	def loop(self, k):
		while not self.stop_threads.is_set():
			# print self.threadnames[k]
			# LOG DATA HERE
			log_data(self.threadnames[k])
			time.sleep(1)

	def combine(self):
		# clear the command to stop
		self.stop_threads.clear()
		for i in range(0, len(control.threads)):
			print 'starting thread'+str(i)+': '+self.threadnames[i]+'...'
			self.threads[i] = Thread(target = self.loop, args = (i,))
			self.threads[i].start()

	def stop(self):
		self.stop_threads.set()
		for i in range(0, len(control.threads)):
			try:
				self.threads[i].join()
				print 'Closing thread '+str(i)+': '+self.threadnames[i]
			except AttributeError:
				print 'Thread '+str(i)+' '+self.threadnames[i]+' is already closed'
			self.threads[i] = None



# INITIALIZATION FUNCTIONS ##############################
def check_dir(folderstr, cruise, payload):
	"""check if the cruise directory exists"""
	if os.path.exists(folderstr+'/'+cruise):
		print 'File structure for cruise '+cruise+' already exists.'
	else:
		print 'Create new file directory for '+cruise+'.'
		os.makedirs(folderstr+'/'+cruise+'/DATA/ACROBAT/RAW')
		os.makedirs(folderstr+'/'+cruise+'/DATA/ACROBAT/PROCESSED')
		for k in payload.keys():
			if "name" in payload[k]:
				os.makedirs(folderstr+'/'+cruise+'/DATA/ACROBAT/RAW/'+payload[k]['name'])

def confirm_dir(folderstr, cruise):
	"""print a confirmation of the folder """
	print 'Data will be output to '+folderstr+'/'+cruise+"/DATA/ACROBAT/RAW"

def print_stop_instructions():
	"""Print out instructions to stop logging"""
	print "*****************************************************************************"
	print "To stop data collection select INTERRUPT from the KERNAL pull down menu above"
	print "*****************************************************************************"

def init_time():
	""" define the time the script starts running """
	starttime = time.time()
	return starttime # return the start time


# data files ###################################
def init_datafile(output_settings, instrument):
    """ initialize and open the data file """
    # find the current directory
    target_dir = '/'.join([output_settings['folder'], output_settings['cruise'], 'Data/Acrobat/RAW',instrument['name']])
    print target_dir
    # get all the files in the directory
    files = os.listdir(target_dir)
    # keep only the dat files
    files = filter(lambda x: x[-4:]=='.dat', files)
    
    # check if there are any .dat files
    if len(files)==0:
        make_new_datafile = 1
    else:
        # sort the files by date
        files.sort(key = lambda x: os.stat(target_dir+'/'+x).st_mtime)
        # pull the latest .dat file
        latest_dat_file = files[-1]
        print 'Latest .dat file: '+latest_dat_file
        # if files more than an hour old
        if time.time()-os.stat(target_dir+'/'+latest_dat_file).st_ctime >datalog_settings['file_length']:
            make_new_datafile = 1
        else:
            make_new_datafile = 0
        
    if make_new_datafile == 1:
        # make a new file
        print 'Last file created more than an hour ago, creating new file....'
        # find the current time and write as string
        current_time = time.strftime("%Y_%m_%d_%H%M", time.gmtime(time.time()))
        # give it a name
        filestr = current_time+output_settings['cruise']+instrument['name']+'RAW.dat' # concatenates strings using 
        print 'Creating '+filestr
        #define write to the new file
        write_mode = 'w'
    elif make_new_datafile == 0:
        # Open file made within the last hour
        filestr = latest_dat_file
        print 'Opening and appending '+latest_dat_file
        # define appending the old file
        write_mode = 'a'
    # now set the target 
    targetstr = '/'.join([output_settings['folder'],output_settings['cruise'],'Data/Acrobat/RAW',instrument['name'],filestr]) # concatencates strings using join
    # open the text file
    fs = open(targetstr, write_mode)
    return fs # return the file id

def close_datafile(fs):
    """close the text file"""
    fs.close() # fs is the output from init_datafile
    print fs.name+' is closed'



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

# acquire data ###################################
def log_data(k):
	global serials, fs, start_time
	# print keyin
	start_dat = start_time
	print start_dat
	while True:
		parse_serialline(serials[k], fs[k])
		if time.time()<start_dat+datalog_settings['file_length']:
				continue
		else:
			fs[k] = init_datafile(output_settings, payload[k])
			start_dat = init_time()

def parse_serialline(ser, fs):
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




# WRAPPER FUNCTION THAT EXECUTES EVERYTHING ##############################
def main():
	root = tk.Tk()
	app = Window(root)
	root.mainloop()

if __name__=='__main__':
	main()				





