import images, hashlib, random, utils
from constants import *
from scripts import objects, maps
#from datetime import datetime, timedelta


class GameFunctions:
	def __init__(self, level=1):
		self.init_game_objects()

		self.shoot_speed = FPS
		self.shoot_iteration = self.shoot_speed

		self.nickname_string = NICKNAME
		self.nickname = NICKNAME
		self.player = None
		self.player_status = 'default'
		self.shouted = False

		self.score = 0

		self.level = level

		self.game_status = 0 # 0 - Menu; 1 - In game

		self.init_optimization()
		#self.main_menu_update()

		self.adding_enemyes_speed = FPS * 1
		self.adding_enemyes_iteration = 0

	def init_game_objects(self):
		self.additional_objects = []
		self.map_objects = []
		self.players = {}
		self.bullets = []
		self.added_bullets = []
		self.grass = []


	def main_menu_update(self, socket = None, get_information = None):
		if not self.main_menu_on:
			main_menu_on = True
			print('\nWelcome to Main menu\n')
			self.additional_objects.append(objects.Button('start_battle', images.get_start_button(), (WIDTH//2 - START_BUTTON_SIZE[0]//2, HEIGHT//2 - START_BUTTON_SIZE[1]//2), START_BUTTON_SIZE))
			if socket:
				while True:
					print(f'Your nickname is: {self.nickname_string}\n')
					options = '1 - show sessions\n' + '2 - create session\n' + '3 - connect to session\n' + '4 - change nickname\n' + '0 - leave\n'
					ch = input(options)

					socket.send('get_sessions_info'.encode(ENCODING))
					sessions_info = get_information()

					if ch == '1':
						print('Avalible_sessions:')
						idx = 0
						for session in sessions_info:
							print(idx, session['session_id'], 'players:', session['players_online'], '/', session['max_players'], 'Map:', session['level'])
							idx += 1
					elif ch == '2':
						while True:
							try:
								session = {'level':min(max(int(input(f'Enter level from 0 to {len(maps.LEVELS)-1} -> ')), 0), len(maps.LEVELS)-1), 
											'max_players':min(max(int(input(f'Max players (2-8) -> ')), 2), MAX_PLAYERS_ON_MAP)}
								break
							except Exception as e:
								print(e)
						session['session_id'] = hashlib.md5(str(random.randint(1, 10**29)).encode()).hexdigest()
						socket.send(utils.prepare_object_to_sending('create_session' + str(session)))
					elif ch == '3':
						if len(sessions_info) == 0:
							print('There is no sessions')
						else:
							session = sessions_info[max(0, min(len(sessions_info)-1, int(input('Enter session id -> '))))]
							session['connect_to_session'] = "1"

							socket.send(utils.prepare_object_to_sending(session))
							res = get_information()

							if res == 'overflowed':
								print('Session is overflowed')
							else:
								return res
					elif ch == '4':
						self.change_nickname(input('Enter new nickname -> '))
					elif ch == '0':
						return 'leave'



	def init_optimization(self):
		self.main_menu_on = False

	def render_map(self, level):
		spawns = []

		for line in maps.LEVELS[level]:
			for obj in range(len(line)):
				crds = (obj*25*AVERAGE_MULTIPLYER, maps.LEVELS[level].index(line)*25*AVERAGE_MULTIPLYER)
				if line[obj] == 'w':
					self.map_objects.append(objects.Wall(crds))
				elif line[obj] == 'r':
					self.map_objects.append(objects.River(crds))
				elif line[obj] == 'g':
					self.grass.append(objects.Grass(crds))
				elif line[obj] == 's':
					spawns.append(crds)

		return spawns

	def start_battle(self):
		self.init_game_objects()
		self.game_status = 1
		self.score = 0
		#self.max_enemyes = self.level + 5
		#self.enemyes = []

		return self.render_map(self.level)

	def stop_battle(self):
		self.game_status = 0
		self.init_optimization()

	def update_battle(self):
		self.shoot_iteration += 1


		'''
		if len(self.enemyes) < self.max_enemyes:
			if self.adding_enemyes_iteration >= self.adding_enemyes_speed:
				self.add_enemy()
				self.adding_enemyes_iteration = -1

		self.adding_enemyes_iteration += 1
		'''


	def shoot(self, tank):
		if tank.rotation == 'forward':
			self.bullets.append(objects.Bullet(tank.rotation, (tank.rect.center[0] - 4*AVERAGE_MULTIPLYER, tank.rect.y - 8*AVERAGE_MULTIPLYER), shooter=tank))
		elif tank.rotation == 'back':
			self.bullets.append(objects.Bullet(tank.rotation, (tank.rect.center[0] - 4*AVERAGE_MULTIPLYER, tank.rect.y + 15*AVERAGE_MULTIPLYER), shooter=tank))
		elif tank.rotation == 'right':
			self.bullets.append(objects.Bullet(tank.rotation, (tank.rect.x + 15*AVERAGE_MULTIPLYER, tank.rect.center[1] - 4*AVERAGE_MULTIPLYER), shooter=tank))
		elif tank.rotation == 'left':
			self.bullets.append(objects.Bullet(tank.rotation, (tank.rect.x - 8*AVERAGE_MULTIPLYER, tank.rect.center[1] - 4*AVERAGE_MULTIPLYER), shooter=tank))

	def change_nickname(self, new_nick):
		self.nickname_string = new_nick[:12:]
		f = open(CONFIG_FILE, 'r')
		data = json.load(f)
		f.close()
		data['NICKNAME'] = new_nick
		f = open(CONFIG_FILE, 'w')
		json.dump(data, f)
		f.close()