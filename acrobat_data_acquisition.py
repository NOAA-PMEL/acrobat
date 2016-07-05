#!/usr/bin/python
# Filename: acrobat_data_acquisition.py

# Import the modules
from acrobat import *

# check the data structure is intact to log data
check_dir(folderstr, cruise, payload)
confirm_dir(folderstr, cruise)

# # open all the defined instruments
# for k in payload.keys():
# 	if "name" in payload[k]:
# 		try:
# 			thread.start_new_thread(run_data_acquisition, (folderstr, cruise, payload[k], datalog_settings))
# 		except:
# 			print 'Thread failed at '+k
#define which instrument to use
serial_in = payload['pieA']

# now acquire data from the instrument
# run_data_acquisition(folderstr, cruise, serial_in, datalog_settings)
try:
	# start a a thread
	print 'start thread'
	t = threading.Thread(target=run_data_acquisition, args=(folderstr, cruise, serial_in, datalog_settings ))
	t.start()
except:
	print 'THREAD FAIL'