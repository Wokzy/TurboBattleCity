import os
import time
import traceback
from constants import CRASH_LOGGING_DIRECTORY

def crash_log():
	print('CRASH LOG CALLED')

	if CRASH_LOGGING_DIRECTORY not in os.listdir():
		os.mkdir(CRASH_LOGGING_DIRECTORY)

	filename = '_'.join(time.asctime().split(' ')) + '.txt'

	with open(f"{CRASH_LOGGING_DIRECTORY}/{filename}", 'w') as f:
		f.write(time.asctime() + '\n\n')
		f.write(traceback.format_exc())
		f.close()

	input()
