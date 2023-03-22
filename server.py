"""
Main game server based on TCP TLS
"""


import sys
import ssl
import json
import random
import socket
import select
import hashlib
import sha256_hashsummer

from datetime import datetime
from ranking.client import RankingClient
from network import prepare_object_to_sending, get_current_timestamp
from constants import SERVER_PORT, SERVER_IP, ENCODING, RUNES_CONFIG,\
						BEGIN_FLAG, END_FLAG, SHOOT_SAVE_DURATION, FINISHED_SESSION_TIMEOUT



NO_VALIDATION = '--no-validation' in sys.argv
RANKED_SERVER_SIGNATURE = input('Enter ranked server signature -> ')


class Server:
	def __init__(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
		# context.load_cert_chain('tbc_cert.pem', 'tbc_key.pem')
		context.load_cert_chain('certificate.pem')

		self.sock = context.wrap_socket(self.sock, server_side=True)
		#self.sock = ssl.wrap_socket(self.sock, server_side=True, certfile="tbc_cert.pem", keyfile="tbc_key.pem")

		self.sock.bind((SERVER_IP, SERVER_PORT))
		self.sock.listen(5)

		self.inputs = [self.sock]
		self.outputs = []

		self.sessions = {}
		self.players_data = {}
		self.unconfirmed_connections = {}

		self.ranking_client = RankingClient()

		print('binded')


	def accept_connection(self, s):
		conn, addr = s.accept()
		conn.setblocking(0)
		self.inputs.append(conn)
		self.unconfirmed_connections[addr] = random.randint(1, 10**10)
		print(f'{addr} is connected')


	def disconnect(self, s):
		if s in self.outputs:
			self.outputs.remove(s)
		self.inputs.remove(s)
		s.shutdown(socket.SHUT_RDWR)
		s.close()
		if s in self.players_data:
			del self.players_data[s]


	def remove_player_from_sessions(self, s):
		for session in self.sessions:
			if s in self.sessions[session]['players_data']:
				del self.sessions[session]['players_data'][s]
				spawn_index = self.sessions[session]['spawns'].index(s)
				self.set_session_spawns_and_scores(session, spawn_index)
				break


	def get_sessions_info(self):
		sessions_info = []
		for session in self.sessions:
				info = {"session_id":session, "players_online":len(self.sessions[session]["players_data"]), 
					"max_players":self.sessions[session]['max_players'], 'level':self.sessions[session]['level']}
				if 'password' in self.sessions[session]:
					info['password'] = self.sessions[session]['password']

				sessions_info.append(info)

		return sessions_info


	def create_session(self, data):
		session = json.loads(data.split('create_session')[1]) # "create_session{'session_id', 'bla', ...}"
		session['players_data'] = {}
		session['runes'] = {'runes':{hashlib.shake_128(str(random.randint(1, 10**21)).encode()).hexdigest(6):{'is_placed':False, 'coords':i} for i in session['runes']}, 'timer':datetime.now()} # is_palace takes rune type, wether rune is placed
		session['creation_time'] = datetime.now()
		session['spawns'] = [True] * session['max_players']
		session['scores'] = {}
		session['shoots'] = {} # {datetime.timestamp}
		session['ranked_users'] = {}
		session['session_status'] = 'waiting'

		if session['ranked']:
			pass

		self.sessions[session['session_id']] = session


	def send_data(self, sock, data:bytes):
		sock.send(BEGIN_FLAG + data + END_FLAG)


	def check_player_files_validation(self, s, data):
		addr = s.getpeername()
		if addr in self.unconfirmed_connections:
			if 'confirmation_response' in data:
				recieved_hash = data.split(' ')[1]
				real_hash = sha256_hashsummer.sum_files_with_extention(solt=self.unconfirmed_connections[addr])

				if recieved_hash == real_hash or NO_VALIDATION:
					self.send_data(s, prepare_object_to_sending('success'))
					print(addr, 'confirmed')
					del self.unconfirmed_connections[addr]
				else:
					print(addr, 'unconfirmed')
					self.send_data(s, prepare_object_to_sending('failed'))

			elif 'confirmation_request' in data:
				with open('sha256_hashsummer.py', 'r') as f:
					cmd = f.read()
					f.close()

				self.send_data(s, prepare_object_to_sending(f'{cmd}\nself.confirmation_result = sum_files_with_extention(solt={self.unconfirmed_connections[addr]})\n'))
			else:
				self.send_data(s, prepare_object_to_sending('Confirm your files before continue'))
			return False

		return True


	def connect_player_to_session(self, s):
		self.players_data[s] = json.loads(self.players_data[s])
		session_id = self.players_data[s]['session_id']
		if self.players_data[s]['reason'] == 'observing':
			self.send_data(s, prepare_object_to_sending({'level':self.sessions[session_id]['level'], 'session_id':session_id, 'observing':1}))
		elif session_id in self.sessions:
			if self.sessions[session_id]['session_status'] == 'finished':
				self.send_data(s, prepare_object_to_sending('session has been finished'))
				return
			elif self.sessions[session_id]['ranked'] and self.sessions[session_id]['session_status'] == 'running':
				self.send_data(s, prepare_object_to_sending('This ranked match has been already started'))
				return

			if 'ranked_user' in self.players_data[s]:
				self.sessions[session_id]['ranked_users'][s] = {'username':self.players_data[s]['ranked_user'], 'score':0}
			elif self.sessions[session_id]['ranked']:
				self.send_data(s, prepare_object_to_sending('you have to be logined to play ranked games'))
				return

			if len(self.sessions[session_id]['players_data']) < self.sessions[session_id]['max_players']:
				availible_spots = [i for i in range(len(self.sessions[session_id]['spawns'])) if self.sessions[session_id]['spawns'][i] == True]
				if len(availible_spots) == 0:
					self.send_data(s, prepare_object_to_sending('Smth wrong with session, try later'))
					return
				spawn_index = random.choice(availible_spots)
				self.sessions[session_id]['spawns'][spawn_index] = s
				self.sessions[session_id]['scores'][spawn_index] = 0
				self.send_data(s, prepare_object_to_sending({'spawn_index':spawn_index, 'level':self.sessions[session_id]['level'], 'session_id':session_id}))
			else:
				self.send_data(s, prepare_object_to_sending('overflowed'))
		else:
			self.send_data(s, prepare_object_to_sending('There is no such session'))


	def collect_other_players_data(self, s):
		data = []
		for key in self.sessions[self.players_data[s]['session_id']]['players_data']:
			if key != s:
				data.append(self.sessions[self.players_data[s]['session_id']]['players_data'][key])
			else:
				data.append(self.sessions[self.players_data[s]['session_id']]['scores'][self.sessions[self.players_data[s]['session_id']]['spawns'].index(s)])
		return data


	def get_availible_runes(self, session_id):
		return [{'rune':self.sessions[session_id]['runes']['runes'][i]['is_placed'], 'coords':self.sessions[session_id]['runes']['runes'][i]['coords'], 'id':i} for i in self.sessions[session_id]['runes']['runes'] if self.sessions[session_id]['runes']['runes'][i]['is_placed'] != False]


	def session_status_update(self, session_id:str):
		if self.sessions[session_id]['session_status'] == 'waiting' or self.sessions[session_id]['session_status'].isnumeric():
			if 'session_status_timer' not in self.sessions[session_id]:
				if not self.sessions[session_id]['ranked'] or len(self.sessions[session_id]['players_data']) == self.sessions[session_id]['max_players']:
						self.sessions[session_id]['session_status_timer'] = datetime.now()
			elif (datetime.now() - self.sessions[session_id]['session_status_timer']).total_seconds() >= 4:
				del self.sessions[session_id]['session_status_timer']
				self.sessions[session_id]['session_status'] = 'running'
			else:
				self.sessions[session_id]['session_status'] = str(int(4 - (datetime.now() - self.sessions[session_id]['session_status_timer']).total_seconds()))
		elif self.sessions[session_id]['session_status'] == 'running':
			if self.sessions[session_id]['score_bound'] in [self.sessions[session_id]['scores'][k] for k in self.sessions[session_id]['scores']]:
				self.sessions[session_id]['session_status'] = 'finished'
				self.sessions[session_id]['finished_timer'] = datetime.now()


	def process_players_data(self, s):
		player_info = {}
		self.players_data[s] = json.loads(self.players_data[s])

		session_id = self.players_data[s]['session_id']

		if 'killer' in self.players_data[s]['player_data']:
			self.sessions[self.players_data[s]['session_id']]['scores'][self.players_data[s]['player_data']['killer']] += 1
		if 'rune_collected' in self.players_data[s]['player_data']:
			collected_rune = self.players_data[s]['player_data']['rune_collected']
			if collected_rune in self.sessions[session_id]['runes']['runes'] and self.sessions[session_id]['runes']['runes'][collected_rune]['is_placed'] != False:
				player_info['rune_collected'] = self.sessions[session_id]['runes']['runes'][collected_rune]['is_placed']
				self.sessions[session_id]['runes']['runes'][collected_rune]['is_placed'] = False


		if self.players_data[s]['player_data']['shouted']['state']:
			timestamp = str(get_current_timestamp())
			self.players_data[s]['player_data']['shouted']['id'] = self.players_data[s]['player_data']['id']
			self.sessions[session_id]['shoots'][timestamp] = self.players_data[s]['player_data']['shouted']
			self.sessions[session_id]['shoots'][timestamp]['timestamp'] = float(timestamp)

		player_info['runes'] = self.get_availible_runes(session_id)
		player_info['runes'] = [{'rune':self.sessions[session_id]['runes']['runes'][i]['is_placed'], 'coords':self.sessions[session_id]['runes']['runes'][i]['coords'], 'id':i} for i in self.sessions[session_id]['runes']['runes'] if self.sessions[session_id]['runes']['runes'][i]['is_placed'] != False]

		self.sessions[session_id]['players_data'][s] = self.players_data[s]['player_data']
		self.sessions[session_id]['players_data'][s]['address'] = f"{s.getpeername()[0]}:{s.getpeername()[1]}" # ip:port
		self.sessions[session_id]['players_data'][s]['connection_time'] = datetime.now().timestamp()
		self.sessions[session_id]['players_data'][s]['score'] = self.sessions[session_id]['scores'][self.players_data[s]['player_data']['spawn_index']]

		if self.sessions[session_id]['ranked']:
			self.sessions[session_id]['ranked_users'][s]['score'] = self.sessions[session_id]['players_data'][s]['score']

		data = {'other_players':self.collect_other_players_data(s), 'player_info':player_info, 'timestamp':get_current_timestamp(),
				'shoots':self.sessions[session_id]['shoots'], 'session_status':self.sessions[session_id]['session_status']}
		self.send_data(s, prepare_object_to_sending(data))


	def process_observing(self, s):
		self.players_data[s] = json.loads(self.players_data[s])
		if self.players_data[s]['session_id'] in self.sessions:
			self.send_data(s, prepare_object_to_sending({'other_players':self.collect_other_players_data(s), 'player_info':{'runes':self.get_availible_runes(self.players_data[s]['session_id'])}}))
		else:
			self.send_data(s, prepare_object_to_sending('value_error'))


	def check_expired_players_and_sessions(self):
		sessions_rm = []
		for session in self.sessions:
			tm_stamp = datetime.now().timestamp()
			players_rm = []
			for player in self.sessions[session]['players_data']:
				if tm_stamp - self.sessions[session]['players_data'][player]['connection_time'] >= 5:
					players_rm.append(player)

			for player in players_rm:
				del self.sessions[session]['players_data'][player]
				spawn_index = self.sessions[session]['spawns'].index(player)
				self.set_session_spawns_and_scores(session, spawn_index)

			if len(self.sessions[session]['players_data']) == 0:
				if (datetime.now() - self.sessions[session]['creation_time']).total_seconds() >= 20:
					sessions_rm.append(session)

			self.session_status_update(session_id = session)
			if self.sessions[session]['session_status'] == 'finished' and (datetime.now() - self.sessions[session]['finished_timer']).total_seconds() > FINISHED_SESSION_TIMEOUT:
				sessions_rm.append(session)
				if self.sessions[session]['ranked']:
					self.count_rankings(session)

		for session in sessions_rm:
			if session in self.sessions:
				del self.sessions[session]


	def count_rankings(self, session_id:str):
		if not self.ranking_client.connected_to_server:
			return

		users = []
		for socket in self.sessions[session_id]['ranked_users']:
			users.append(self.sessions[session_id]['ranked_users'][socket])

		self.ranking_client.send_information({'request':'count_rankings', 'signature':RANKED_SERVER_SIGNATURE, 'users':users})


	def set_session_spawns_and_scores(self, session, index):
		self.sessions[session]['spawns'][index] = True
		self.sessions[session]['scores'][index] = 0


	def update_sessions(self):
		now = datetime.now()
		for session in self.sessions:
			if (now - self.sessions[session]['runes']['timer']).total_seconds() >= RUNES_CONFIG['spawn_timer'] and self.sessions[session]['session_status'] == 'running':
				self.sessions[session]['runes']['timer'] = now
				availible_spots = [i for i in self.sessions[session]['runes']['runes'] if self.sessions[session]['runes']['runes'][i]['is_placed'] == False]
				if availible_spots:
					self.sessions[session]['runes']['runes'][random.choice(availible_spots)]['is_placed'] = random.choice(RUNES_CONFIG['runes'])

			del_names = []

			for shoot in self.sessions[session]['shoots']:
				if get_current_timestamp() - float(shoot) >= SHOOT_SAVE_DURATION:
					del_names.append(shoot)

			for name in del_names:
				del self.sessions[session]['shoots'][name]



	def main(self):

		while self.inputs:
			self.iteration = 1
			self.readable, self.writable, self.exceptional = select.select(self.inputs, self.outputs, self.inputs)

			for s in self.readable:
				if s == self.sock:

					#if len(self.players_data) >= 4:
					#	continue
					try:
						self.accept_connection(s)
					except:
						continue
				else:
					try:
						data = s.recv(1024)
					except:
						self.disconnect(s)
						continue

					if data:
						#print(f'Recieved {data.decode("utf-8")} | from {s.getpeername()[0]}:{s.getpeername()[1]}')
						data = data.decode(ENCODING)
						addr = s.getpeername()
						if not self.check_player_files_validation(s, data):
							continue

						if 'create_session' in data:
							self.create_session(data)
						else:
							self.players_data[s] = data
							if s not in self.outputs:
								self.outputs.append(s)
					else:
						self.disconnect(s)

			for s in self.writable:
				if s in self.outputs:
					self.outputs.remove(s)
				if self.players_data[s] == 'get_sessions_info':
					self.remove_player_from_sessions(s)
					self.send_data(s, prepare_object_to_sending(self.get_sessions_info()))
				elif 'connect_to_session' in self.players_data[s]:
					self.connect_player_to_session(s)
				elif 'player_data' in self.players_data[s]:
					self.process_players_data(s)
				elif 'observing' in self.players_data[s]:
					self.process_observing(s)

			for s in self.exceptional:
				self.disconnect(s)

			self.update_sessions()
			self.check_expired_players_and_sessions()

			self.iteration += 1

#try:
Server().main()
#except KeyboardInterrupt:
# 	exit()
# except Exception as e:
# 	print(e)
# 	input()
