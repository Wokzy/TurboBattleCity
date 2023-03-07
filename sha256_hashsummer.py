#import os
#import hashlib

def get_sum_of_file(filename):
	import hashlib
	with open(filename, 'rb') as f:
		data = f.read()
		f.close()

	return hashlib.sha256(data).hexdigest()

def sum_files_with_extention(extentions=['.py', '.png', '.exe'], dirs=[], solt=0):
	import os
	import hashlib
	#string = '{solt}'

	if './' not in dirs:
		if dirs == []:
			dirs = ['scripts'] + ['sprites/' + obj for obj in os.listdir('sprites') if '.' not in obj]
		dirs.insert(0, './')
		if '__pycache__' in dirs:
			dirs.remove('__pycache__')

	dirs.sort()

	sm = 0

	for add_dir in dirs:
		for file in sorted(os.listdir(add_dir)):
			for extention in extentions:
				if extention == file[-len(extention)::]:
					with open(f'{add_dir}/{file}', 'rb') as f:
						data = f.read()
						f.close()
					sm += int(hashlib.sha256(data).hexdigest(), base=16)
	return hashlib.sha256(f'{solt}{sm}'.encode()).hexdigest()
