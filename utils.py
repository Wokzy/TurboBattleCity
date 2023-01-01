import random
import hashlib

from constants import *

def prepare_object_to_sending(obj, split_data=False):
	if split_data:
		string = str(obj) + '\n'
	else:
		string = str(obj)
	return string.replace("'", '"').encode(ENCODING)



def gen_random_shake(length=16, seed=(0, 10**24)):
	return hashlib.shake_128(f'{random.randint(*seed)}'.encode()).hexdigest(length)

gen_random_hash = gen_random_shake
