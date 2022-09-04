#import os
#import hashlib

def get_sum_of_file(filename):
	import hashlib
	with open(filename, 'rb') as f:
		data = f.read()
		f.close()

	return hashlib.sha256(data).hexdigest()

def sum_files_with_extention(extention='.py', dirs=['scripts'], solt=0):
	import os
	import hashlib
	string = '{solt}'

	if './' not in dirs:
		dirs.insert(0, './')

	for add_dir in dirs:
		for file in os.listdir(add_dir):
			if extention in file[-len(extention)::]:
				with open(f'{add_dir}/{file}', 'rb') as f:
					data = f.read()
					f.close()
				string += hashlib.sha256(data).hexdigest() # bebra

	return hashlib.sha256(string.encode()).hexdigest()