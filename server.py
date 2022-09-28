import socket, select, time, json, utils, random, sha256_hashsummer
from constants import SERVER_PORT, SERVER_IP
from datetime import datetime


ENCODING = 'utf-8'

class Server:
	def __init__(self):
		self.sock = socket.socket()
		self.sock.bind((SERVER_IP, SERVER_PORT))
		self.sock.listen(5)
		self.inputs = [self.sock]
		self.outputs = []

		self.sessions = {}
		self.players_data = {}
		self.unconfirmed_connections = {}

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
		return [{"session_id":session, "players_online":len(self.sessions[session]["players_data"]), 
					"max_players":self.sessions[session]['max_players'], 'level':self.sessions[session]['level']} for session in self.sessions]


	def create_session(self, data):
		session = json.loads(data.split('create_session')[1]) # "create_session{'session_id', 'bla', ...}"
		session['players_data'] = {}
		session['creation_time'] = datetime.now()
		self.sessions[session['session_id']] = session
		session['spawns'] = [True] * session['max_players']
		session['scores'] = {}


	def check_player_files_validation(self, s, data):
		addr = s.getpeername()
		if addr in self.unconfirmed_connections:
			if 'confirmation_response' in data:
				recieved_hash = data.split(' ')[1]
				real_hash = sha256_hashsummer.sum_files_with_extention(solt=self.unconfirmed_connections[addr])

				if recieved_hash == real_hash:
					s.send(utils.prepare_object_to_sending('success'))
					print(addr, 'confirmed')
					del self.unconfirmed_connections[addr]
				else:
					print(addr, 'unconfirmed')
					s.send(utils.prepare_object_to_sending('failed'))

			elif 'confirmation_request' in data:
				with open('sha256_hashsummer.py', 'r') as f:
					cmd = f.read()
					f.close()

				s.send(utils.prepare_object_to_sending(f'{cmd}\nself.confirmation_result = sum_files_with_extention(solt={self.unconfirmed_connections[addr]})'))
			else:
				s.send(utils.prepare_object_to_sending('Confirm your files before continue'))
			return False

		return True


	def connect_player_to_session(self, s):
		self.players_data[s] = json.loads(self.players_data[s])
		session_id = self.players_data[s]['session_id']
		if len(self.sessions[session_id]['players_data']) < self.sessions[session_id]['max_players']:
			spawn_index = random.choice([i for i in range(len(self.sessions[session_id]['spawns'])) if self.sessions[session_id]['spawns'][i] == True])
			self.sessions[session_id]['spawns'][spawn_index] = s
			self.sessions[session_id]['scores'][spawn_index] = 0
			s.send(utils.prepare_object_to_sending({'spawn_index':spawn_index, 'level':self.sessions[session_id]['level'], 'session_id':session_id}))
		else:
			s.send(utils.prepare_object_to_sending('overflowed'))


	def process_players_data(self, s):
		self.players_data[s] = json.loads(self.players_data[s])
		if 'killer' in self.players_data[s]['player_data']:
			self.sessions[self.players_data[s]['session_id']]['scores'][self.players_data[s]['player_data']['killer']] += 1
		self.sessions[self.players_data[s]['session_id']]['players_data'][s] = self.players_data[s]['player_data']
		self.sessions[self.players_data[s]['session_id']]['players_data'][s]['address'] = f"{s.getpeername()[0]}:{s.getpeername()[1]}" # ip:port
		self.sessions[self.players_data[s]['session_id']]['players_data'][s]['connection_time'] = datetime.now().timestamp()
		self.sessions[self.players_data[s]['session_id']]['players_data'][s]['score'] = self.sessions[self.players_data[s]['session_id']]['scores'][self.players_data[s]['player_data']['spawn_index']]
		data = []
		for key in self.sessions[self.players_data[s]['session_id']]['players_data']:
			if key != s:
				data.append(self.sessions[self.players_data[s]['session_id']]['players_data'][key])
			else:
				data.append(self.sessions[self.players_data[s]['session_id']]['scores'][self.sessions[self.players_data[s]['session_id']]['spawns'].index(s)])
		s.send(utils.prepare_object_to_sending(data))


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

		for session in sessions_rm:
			del self.sessions[session]


	def set_session_spawns_and_scores(self, session, index):
		self.sessions[session]['spawns'][index] = True
		self.sessions[session]['scores'][index] = 0


	def main(self):

		while self.inputs:
			self.iteration = 1
			self.readable, self.writable, self.exceptional = select.select(self.inputs, self.outputs, self.inputs)

			for s in self.readable:
				if s == self.sock:

					#if len(self.players_data) >= 4:
					#	continue

					self.accept_connection(s)
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
				self.outputs.remove(s)
				if self.players_data[s] == 'get_sessions_info':
					self.remove_player_from_sessions(s)
					s.send(utils.prepare_object_to_sending(self.get_sessions_info()))
				elif 'connect_to_session' in self.players_data[s]:
					self.connect_player_to_session(s)
				elif 'player_data' in self.players_data[s]:
					self.process_players_data(s)

			for s in self.exceptional:
				self.disconnect(s)

			self.check_expired_players_and_sessions()

			self.iteration += 1


Server().main()
