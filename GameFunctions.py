import images, hashlib, random, utils
from constants import *
from scripts import objects, maps
#from datetime import datetime, timedelta


class GameFunctions:
	def __init__(self, level=1):
		self.additional_objects = []
		self.players = {}
		self.bullets = []
		self.added_bullets = []
		self.grass = []

		self.shoot_speed = FPS
		self.shoot_iteration = self.shoot_speed

		self.player = None
		self.player_status = 'default'
		self.shouted = False

		self.level = level

		self.game_status = 0 # 0 - Menu; 1 - In game

		self.init_optimization()
		#self.main_menu_update()

		self.adding_enemyes_speed = FPS * 1
		self.adding_enemyes_iteration = 0


	def main_menu_update(self, socket = None, get_information = None):
		if not self.main_menu_on:
			main_menu_on = True
			print('\nWelcome to Main menu\n')
			self.additional_objects.append(objects.Button('start_battle', images.get_start_button(), (WIDTH//2 - START_BUTTON_SIZE[0]//2, HEIGHT//2 - START_BUTTON_SIZE[1]//2), START_BUTTON_SIZE))
			if socket:
				while True:
					options = '1 - show sessions\n' + '2 - create session\n' + '3 - connect to session\n' + '4 - leave\n'
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
											'max_players':10}
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
						return 'leave'



	def init_optimization(self):
		self.main_menu_on = False

	def start_battle(self):
		self.game_status = 1
		#self.max_enemyes = self.level + 5
		#self.enemyes = []
		self.additional_objects = []

		self.map_objects = []

		spawns = []

		for line in maps.LEVELS[self.level]:
			for obj in range(len(line)):
				crds = (obj*25*AVERAGE_MULTIPLYER, maps.LEVELS[self.level].index(line)*25*AVERAGE_MULTIPLYER)
				if line[obj] == 'w':
					self.map_objects.append(objects.Wall(crds))
				elif line[obj] == 'r':
					self.map_objects.append(objects.River(crds))
				elif line[obj] == 'g':
					self.grass.append(objects.Grass(crds))
				elif line[obj] == 's':
					spawns.append(crds)

		return spawns

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
			self.bullets.append(objects.Bullet(tank.rotation, (tank.rect.center[0] - 4*AVERAGE_MULTIPLYER, tank.rect.y - 8*AVERAGE_MULTIPLYER)))
		elif tank.rotation == 'back':
			self.bullets.append(objects.Bullet(tank.rotation, (tank.rect.center[0] - 4*AVERAGE_MULTIPLYER, tank.rect.y + 15*AVERAGE_MULTIPLYER)))
		elif tank.rotation == 'right':
			self.bullets.append(objects.Bullet(tank.rotation, (tank.rect.x + 15*AVERAGE_MULTIPLYER, tank.rect.center[1] - 4*AVERAGE_MULTIPLYER)))
		elif tank.rotation == 'left':
			self.bullets.append(objects.Bullet(tank.rotation, (tank.rect.x - 8*AVERAGE_MULTIPLYER, tank.rect.center[1] - 4*AVERAGE_MULTIPLYER)))