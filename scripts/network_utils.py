from constants import ENCODING


def prepare_object_to_sending(obj, split_data=False):
	if split_data:
		string = str(obj) + '\n'
	else:
		string = str(obj)
	return string.replace("'", '"').encode(ENCODING)
