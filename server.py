import socket, select, time, json, utils, random, sha256_hashsummer
from constants import SERVER_PORT, SERVER_IP
from datetime import datetime

sock = socket.socket()
sock.bind((SERVER_IP, SERVER_PORT))
sock.listen(5)
inputs = [sock]
outputs = []

ENCODING = 'utf-8'

sessions = {}
players_data = {}
unconfirmed_connections = {}
#level = 0

print('binded')

while inputs:
	iteration = 1
	readable, writable, exceptional = select.select(inputs, outputs, inputs)

	for s in readable:
		if s == sock:

			if len(players_data) >= 4:
				continue

			conn, addr = s.accept()
			conn.setblocking(0)
			inputs.append(conn)
			unconfirmed_connections[addr] = random.randint(1, 10**10)
			print(f'{addr} is connected')
		else:
			try:
				data = s.recv(1024)
			except:
				if s in outputs:
					outputs.remove(s)
				inputs.remove(s)
				continue

			if data:
				#print(f'Recieved {data.decode("utf-8")} | from {s.getpeername()[0]}:{s.getpeername()[1]}')
				data = data.decode(ENCODING)
				addr = s.getpeername()
				if addr in unconfirmed_connections:

					if 'confirmation_response' in data:
						recieved_hash = data.split(' ')[1]
						real_hash = sha256_hashsummer.sum_files_with_extention(solt=unconfirmed_connections[addr])

						if recieved_hash == real_hash:
							s.send(utils.prepare_object_to_sending('success'))
							print(addr, 'confirmed')
							del unconfirmed_connections[addr]
						else:
							print(addr, 'unconfirmed')
							s.send(utils.prepare_object_to_sending('failed'))

					elif 'confirmation_request' in data:
						with open('sha256_hashsummer.py', 'r') as f:
							data = f.read()
							f.close()

						s.send(utils.prepare_object_to_sending(f'{data}\nself.confirmation_result = sum_files_with_extention(solt={unconfirmed_connections[addr]})'))
					else:
						s.send(utils.prepare_object_to_sending('Confirm your files before continue'))
					continue

				if 'create_session' in data:
					session = json.loads(data.split('create_session')[1]) # "create_session{'session_id', 'bla', ...}"
					session['players_data'] = {}
					session['creation_time'] = datetime.now()
					sessions[session['session_id']] = session
					session['spawns'] = [True] * session['max_players']
					session['scores'] = {}
				else:
					players_data[s] = data
					if s not in outputs:
						outputs.append(s)
			else:
				if s in outputs:
					outputs.remove(s)
				inputs.remove(s)
				s.shutdown(socket.SHUT_RDWR)
				s.close()
				if s in players_data:
					del players_data[s]

	for s in writable:
		#time.sleep(0.2)
		outputs.remove(s)
		if players_data[s] == 'get_sessions_info':
			for session in sessions:
				if s in sessions[session]['players_data']:
					del sessions[session]['players_data'][s]
					spawn_index = sessions[session]['spawns'].index(s)
					sessions[session]['spawns'][spawn_index] = True
					sessions[session]['scores'][spawn_index] = 0
					break

			session_info = [{"session_id":session, "players_online":len(sessions[session]["players_data"]), 
							"max_players":sessions[session]['max_players'], 'level':sessions[session]['level']} for session in sessions]
			#print(session_info)
			s.send(utils.prepare_object_to_sending(session_info))
		elif 'connect_to_session' in players_data[s]:
			#print(players_data[s])
			players_data[s] = json.loads(players_data[s])
			session_id = players_data[s]['session_id']
			if len(sessions[session_id]['players_data']) < sessions[session_id]['max_players']:
				spawn_index = sessions[session_id]['spawns'].index(True)
				sessions[session_id]['spawns'][spawn_index] = s
				sessions[session_id]['scores'][spawn_index] = 0
				info = {'spawn_index':spawn_index, 'level':sessions[session_id]['level'], 'session_id':session_id}
				s.send(utils.prepare_object_to_sending(info))
			else:
				s.send(utils.prepare_object_to_sending('overflowed'))
		elif 'player_data' in players_data[s]:
			#print(players_data[s])
			players_data[s] = json.loads(players_data[s])
			if 'killer' in players_data[s]['player_data']:
				sessions[players_data[s]['session_id']]['scores'][players_data[s]['player_data']['killer']] += 1
			sessions[players_data[s]['session_id']]['players_data'][s] = players_data[s]['player_data']
			sessions[players_data[s]['session_id']]['players_data'][s]['address'] = f"{s.getpeername()[0]}:{s.getpeername()[1]}" # ip:port
			sessions[players_data[s]['session_id']]['players_data'][s]['connection_time'] = datetime.now().timestamp()
			sessions[players_data[s]['session_id']]['players_data'][s]['score'] = sessions[players_data[s]['session_id']]['scores'][players_data[s]['player_data']['spawn_index']]
			data = []
			for key in sessions[players_data[s]['session_id']]['players_data']:
				if key != s:
					data.append(sessions[players_data[s]['session_id']]['players_data'][key])
				else:
					data.append(sessions[players_data[s]['session_id']]['scores'][sessions[players_data[s]['session_id']]['spawns'].index(s)])
			s.send(utils.prepare_object_to_sending(data))

	for s in exceptional:
		if s in outputs:
			outputs.remove(s)
		inputs.remove(s)
		s.shutdown(socket.SHUT_RDWR)
		s.close()
		del players_data[s]

	sessions_rm = []
	for session in sessions:
		tm_stamp = datetime.now().timestamp()
		players_rm = []
		for player in sessions[session]['players_data']:
			if tm_stamp - sessions[session]['players_data'][player]['connection_time'] >= 5:
				players_rm.append(player)

		for player in players_rm:
			del sessions[session]['players_data'][player]
			spawn_index = sessions[session]['spawns'].index(player)
			sessions[session]['spawns'][spawn_index] = True
			sessions[session]['scores'][spawn_index] = 0

		if len(sessions[session]['players_data']) == 0:
			if (datetime.now() - sessions[session]['creation_time']).total_seconds() >= 20:
				sessions_rm.append(session)

	for session in sessions_rm:
		del sessions[session]

	iteration += 1