"""
Network supporting module with utils and socket connectivity
"""

import sys
import ssl
import json
import socket as socket_lib

from constants import ENCODING, SERVER_IP, SERVER_PORT, RECIEVE_BYTES_AMOUNT, \
						TICK_RATE, END_FLAG, BEGIN_FLAG


def prepare_object_to_sending(obj, split_data=False, json_type=True):
	"""
	formats string to prepare for sending
	"""

	if split_data:
		string = str(obj) + '\n'
	else:
		string = str(obj)

	return string.replace("'", '"').encode(ENCODING)


class Client:
	def __init__(self):
		self.server = (SERVER_IP, SERVER_PORT)
		self.initialize_socket()
		self.files_validation()

		self.player_info = None


	def initialize_socket(self):
		"""
		Starting socket and connecting to the server
		"""

		self.socket = socket_lib.socket(socket_lib.AF_INET, socket_lib.SOCK_STREAM)
		self.socket.setsockopt(socket_lib.SOL_SOCKET, socket_lib.SO_REUSEADDR, 1)
		self.socket.settimeout(5)

		context = ssl.SSLContext(ssl.PROTOCOL_TLS)
		context.load_verify_locations(cadata=ssl.get_server_certificate(self.server))

		self.socket = context.wrap_socket(self.socket)

		self.socket.connect(self.server)
		print('Cipher used:', self.socket.cipher())


	def files_validation(self):
		"""
		Part of anti-cheat. Function requests validation requets to be accepted by server, wethter responce
		will be ok.
		"""

		self.socket.send(prepare_object_to_sending('confirmation_request', json_type=False))
		command = self.get_information(parse=False)
		exec(command)
		print(self.confirmation_result)
		self.socket.send(prepare_object_to_sending(f'confirmation_response {self.confirmation_result}', json_type=False))


		if self.get_information(parse=False) == 'success':
			print('Files confimation successfull')
			return True

		self.disconnect()
		input('Files confimation failed; check wether game is up to date; press enter to quit')
		sys.exit()


	'''
	def server_updating_thread(self, gf):
		"""Run as thread"""

		server_update_time = 1 / TICK_RATE
		server_update_timer = datetime.now()

		def _it_is_time_to_update_server(self):
			return (datetime.now() - server_update_timer).total_seconds() >= server_update_time

		while True:
			if _it_is_time_to_update_server():
				if gf.game_status == 1:
					pass
	'''



	def get_information(self=None, parse=True):
		info = self.socket.recv(RECIEVE_BYTES_AMOUNT)
		while not info.endswith(END_FLAG):
			info += self.socket.recv(RECIEVE_BYTES_AMOUNT)

		if not info.startswith(BEGIN_FLAG):
			raise RuntimeError('Recieving message error: message starts not appropriately')

		info = info[len(BEGIN_FLAG):-len(END_FLAG):].decode(ENCODING)

		if parse and ('[' in info or '{' in info):
			return json.loads(info)
		return info


	def send_information(self, info):
		"""Sending data after preparing"""
		self.socket.send(prepare_object_to_sending(info))


	def send_player_data(self):
		"""Makes player info JSON and sends it"""

		info = {'session_id':self.session_id, 'player_data':self.player_data}
		self.send_information(info)


	def disconnect(self):
		"""Disconnection from server and closing socket"""

		if self.socket.fileno() != -1:
			self.socket.shutdown(socket_lib.SHUT_RDWR)
			self.socket.close()
