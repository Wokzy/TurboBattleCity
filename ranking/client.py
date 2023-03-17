"""Ranked system connector script for player"""

import json

from network import Client
from constants import RANKED_SERVER_ADRESS


class RankingClient(Client):
	"""
	Client class for player, supporting connection to stats server
	"""

	def __init__(self):
		"""Connection to the server"""

		self.user = None

		try:
			super().__init__(server = RANKED_SERVER_ADRESS, validation = False)
			self.connected_to_server = True
		except ConnectionRefusedError:
			print('Cannot connect to raking server')
			self.connected_to_server = False


	def send_information(self, info:dict):
		"""Sending info rebuild on json"""

		try:
			self.socket.send(json.dumps(info).encode())
		except ValueError:
			self.connect()
			self.socket.send(json.dumps(info).encode())


	def get_information(self):
		"""Rebuild on json without flags""" # DANGEROUS!

		return json.loads(self.socket.recv(65536).decode())


	def main_menu(self):
		"""Main CLI menu for ranking system"""

		attributes = ['quit', 'login']#, 'get_self_stats', 'get_top_players']

		while True:
			print('\n', '\n'.join([f'{i} - {attributes[i]}' for i in range(len(attributes))]), sep='')

			request = input('-> ')
			if not request.isnumeric() or int(request) not in range(0, len(attributes)):
				print("Invalid request")
				continue

			if attributes[int(request)] == 'quit':
				return

			if not getattr(self, attributes[int(request)])():
				return


	def login(self):
		"""Get user credentials and login"""

		username = input('Enter username -> ')
		password = input('Enter password -> ')

		self.send_information({'request':'login', 'username':username, 'password':password})
		result = self.get_information()

		print(result['content'])
		if not result['status']:
			self.send_information({'request':'get_user_stats', 'username':username})
			self.user = {'username':username, 'password':password, 'stats':self.get_information()}

		return result['status']
