import utils

from constants import *
from scripts import network_utils as ntwu


class Menu:
	def __init__(self, engine):
		self.engine = engine
		self.gf = GameFunctions.GameFunctions()


	def interact(self):
		pass


	def connect_to_session(self):
		if len(sessions_info) == 0:
			print('There is no sessions')
			return

		session = sessions_info[max(0, min(len(sessions_info)-1, int(input('Enter session id -> '))))]
		if 'password' in session:
			attempts = 3
			for i in range(1, attempts+1):
				if hashlib.md5(input(f'Enter session password ({attempts - i} attempts left) -> ').encode()).hexdigest() == session['password']:
					break
				elif i == attempts:
					return
		session['connect_to_session'] = "1"
		session['reason'] = reason

		res = self.engine.network_handler.connect_to_session(sessions_info = session)
		if res in NETWORK_ERRORS:
			print(NETWORK_ERRORS[res])
		else:
			return res


	def create_session(self):
		while True:
			try:
				level, max_players = self.input_map_level()
				max_players_choice = input(f'Max players (2-{max_players}) -> ')
				if max_players_choice.isnumeric():
					max_players = min(max(int(max_players_choice), 2), max_players)

				session = {'level': level, 'runes':self.get_coords(level=level, obj = maps.RUNE, TYPE=list, move=(RUNE_SIZE[0]//2, RUNE_SIZE[1]//2)),
							'max_players':max_players}

				password = input('Enter password (leave empty for no password) -> ')
				if password:
					session['password'] = hashlib.md5(password.encode()).hexdigest()
				break
			except Exception as e:
				print(e)
		session['session_id'] = utils.generate_session_id()
		self.engine.network_handler.socket.send(ntwu.prepare_object_to_sending('create_session' + str(session)))

	def observe_session(self, sessions_info):
		res = +self.connect_to_session(sessions_info, reason='observing')
		if res != None:
			gf.init_game_objects()
			gf.game_status = 3
			gf.render_map(res['level'])

		res['observing'] = True
		return res



def interact(engine):
	Menu(engine).interact()
