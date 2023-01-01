import ssl
import time
import socket
import threading

from scripts import network_utils as ntwu
from constants import *

class NetworkHandler(threading.Thread): # run = NetworkHandler.start()
	def __init__(self):
		threading.Thread.__init__(self, daemon=True)
		self.server = (SERVER_IP, SERVER_PORT)
		self.data_to_send = {}
		self.recieved_data = {}
		self.session_id = None
		self.player_data = None
		self.other_players_data = None

		self.server_update_time = 1 / TICK_RATE


	def run(self):
		while True:
			self.update()
			time.sleep(self.server_update_time)


	def update(self):
		if self.data_to_send != {}:
			for key in self.data_to_send:
				self.send_information(self.data_to_send[key])
				self.recieved_data[key] = self.get_information()
				del self.data_to_send[key]
		if self.player_data and self.session_id:
			self.send_player_data()
			self.other_players_data = self.get_information()


	def stable_connection(self):
		self.connect()
		return self.do_handshake()


	def connect(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		context = ssl.SSLContext(ssl.PROTOCOL_TLS)
		context.verify_mode = ssl.CERT_REQUIRED
		context.load_verify_locations(cafile='tbc_cert.pem', capath=None, cadata=None)

		self.socket = context.wrap_socket(self.socket)

		#self.socket = ssl.wrap_socket(self.socket, certfile="tbc_cert.pem", keyfile="tbc_key.pem")
		self.socket.connect(self.server)
		print('Cipher used:', self.socket.cipher())


	def do_handshake(self):
		self.socket.send(ntwu.prepare_object_to_sending('confirmation_request'))
		command = self.get_information(parse=False)
		exec(command)
		self.socket.send(ntwu.prepare_object_to_sending(f'confirmation_response {self.confirmation_result}'))
		if self.get_information(parse=False) == 'success':
			return True, 'Files confimation successfull'
		else:
			self.disconnect()
			return False, 'Files confimation failed; check wether game is up to date; press enter to quit'

	'''
	def connect_to_session(self, sessions_info, reason='playing'):
		self.socket.send(utils.prepare_object_to_sending(sessions_info))
		return self.get_information()
	'''


	def get_information(self=None, parse=True):
		info = self.socket.recv(1024).decode(ENCODING)
		if parse and ('[' in info or '{' in info):
			return json.loads(info)
		return info


	def send_information(self, info):
		self.socket.send(ntwu.prepare_object_to_sending(info))


	def send_player_data(self):
		info = {'session_id':self.session_id, 'player_data':self.player_data}
		self.send_information(info)


	def disconnect(self):
		if self.socket.fileno() != -1:
			self.socket.shutdown(socket.SHUT_RDWR)
			self.socket.close()


	def send(self, key, data):
		self.data_to_send[key] = data
		self.recieved_data[key] = None
