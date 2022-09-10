#import os
#import hashlib

def get_sum_of_file(filename):
	import hashlib
	with open(filename, 'rb') as f:
		data = f.read()
		f.close()

	return hashlib.sha256(data).hexdigest()

def sum_files_with_extention(extentions=['.py', '.png'], dirs=[], solt=0):
	import os
	import hashlib
	string = '{solt}'

	if './' not in dirs:
		if dirs == []:
			dirs = ['scripts'] + ['sprites/' + obj for obj in os.listdir('sprites') if '.' not in obj]
		dirs.insert(0, './')
		if '__pycache__' in dirs:
			dirs.remove('__pycache__')

	dirs.sort()

	for add_dir in dirs:
		for file in sorted(os.listdir(add_dir)):
			for extention in extentions:
				if extention == file[-len(extention)::]:
					with open(f'{add_dir}/{file}', 'rb') as f:
						data = f.read()
						f.close()
					string += hashlib.sha256(data).hexdigest() # bebra
	return hashlib.sha256(string.encode()).hexdigest()