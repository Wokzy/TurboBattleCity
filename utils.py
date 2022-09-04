from constants import *

def prepare_object_to_sending(obj):
	return str(obj).replace("'", '"').encode(ENCODING)