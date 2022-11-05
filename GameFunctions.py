import utils
import pygame
import images
import random
import hashlib

from constants import *
from scripts import objects, maps
from datetime import datetime, timedelta


class GameFunctions:
	def __init__(self, level=1):
		self.init_game_objects()

		self.nickname_string = NICKNAME
		self.nickname = NICKNAME
		self.player = None
		self.player_status = 'default'
		self.score = 0

		self.level = level

		self.game_status = 0 # 0 - Menu; 1 - In game

		self.init_optimization()
		#self.main_menu_update()

		self.adding_enemyes_speed = FPS * 1
		self.adding_enemyes_iteration = 0

	def init_game_objects(self):
		self.additional_objects = [objects.Button('leave_session', images.get_leave_session_button(), (WIDTH - LEAVE_SESSION_BUTTON_SIZE[0], 0), LEAVE_SESSION_BUTTON_SIZE)]
		self.map_objects = []
		self.players = {}
		self.bullets = []
		self.runes = []
		self.active_runes = {i:False for i in RUNES_CONFIG['runes']}
		self.added_bullets = []
		self.grass = []
		self.ammunition = AMMUNITION_SIZE
		self.ammunition_string = str(self.ammunition)
		self.boost_bar = images.get_boost_bar()['bar']
		self.boost_bar_background = images.get_boost_bar()['background']
		self.death_timer = None


	def input_map_level(self):
		while True:
			try:
				level_id = min(max(int(input(f'Enter level from 0 to {len(maps.LEVELS)-1} -> ')), 0), len(maps.LEVELS)-1)
				max_players = sum([row.count('s') for row in maps.LEVELS[level_id]])
				return level_id, max_players
			except Exception as e:
				pass


	def main_menu_update(self, socket = None, get_information = None):
		if not self.main_menu_on:
			#self.main_menu_on = True
			print('\nWelcome to Main menu\n')
			#self.additional_objects.append(objects.Button('start_battle', images.get_start_button(), (WIDTH//2 - START_BUTTON_SIZE[0]//2, HEIGHT//2 - START_BUTTON_SIZE[1]//2), START_BUTTON_SIZE))
			if socket:
				while True:
					print(f'Your nickname is: {self.nickname_string}\n')
					options = '1 - show sessions\n' + '2 - create session\n' + '3 - connect to session\n' + '4 - change nickname\n' + \
								'5 - map preview\n' + '6 - observe game\n' + '0 - leave\n'
					ch = input(options)

					socket.send('get_sessions_info'.encode(ENCODING))
					sessions_info = get_information()

					if ch == '1':
						self.show_avalible_sessions(sessions_info)
					elif ch == '2':
						self.create_session(socket)
					elif ch == '3':
						self.show_avalible_sessions(sessions_info)
						return self.connect_to_session(socket, sessions_info, get_information)
					elif ch == '4':
						self.change_nickname(input('Enter new nickname -> '))
					elif ch == '5':
						self.map_preview()
						return 'map_preview'
					elif ch == '6':
						return self.observe_session(socket, sessions_info, get_information)
					elif ch == '0':
						return 'leave'


	def show_avalible_sessions(self, sessions_info):
		print('Avalible_sessions:')
		idx = 0
		for session in sessions_info:
			print(idx, session['session_id'], 'players:', session['players_online'], '/', session['max_players'],
			'Map:', session['level'], f'password: {("No", "Yes")["password" in session]}')
			idx += 1

	def create_session(self, socket):
		while True:
			try:
				level, max_players = self.input_map_level()
				session = {'level': level, 'runes':self.get_coords(level=level, obj = maps.RUNE, TYPE=list),
							'max_players':min(max(int(input(f'Max players (2-{max_players}) -> ')), 2), max_players)}
				password = input('Enter password (leave empty for no password) -> ')
				if password:
					session['password'] = hashlib.md5(password.encode()).hexdigest()
				break
			except Exception as e:
				print(e)
		session['session_id'] = hashlib.md5(str(random.randint(1, 10**29)).encode()).hexdigest()
		socket.send(utils.prepare_object_to_sending('create_session' + str(session)))


	def connect_to_session(self, socket, sessions_info, get_information, reason='playing'):
		if len(sessions_info) == 0:
			print('There is no sessions')
		else:
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

			socket.send(utils.prepare_object_to_sending(session))
			res = get_information()

			if res == 'overflowed':
				print('Session is overflowed')
			elif res == 'error':
				print('Unexpected error occured during connection')
			else:
				return res


	def observe_session(self, socket, sessions_info, get_information):
		res = self.connect_to_session(socket, sessions_info, get_information, reason='observing')
		if res != None:
			self.init_game_objects()
			self.game_status = 3
			self.render_map(res['level'])

		res['observing'] = True
		return res



	def init_optimization(self):
		self.main_menu_on = False


	def map_preview(self):
		self.game_status = 2
		self.map_objects = []
		self.grass = []
		self.init_game_objects()
		self.render_map(self.input_map_level()[0], True)


	def get_coords(self, level, obj, TYPE = tuple):
		coords = []
		for line in range(len(maps.LEVELS[level])):
			for o in range(len(maps.LEVELS[level][line])):
				if maps.LEVELS[level][line][o] == obj:
					coords.append(TYPE((o*MAP_COORD_SHIFT[0], line*MAP_COORD_SHIFT[1])))

		return coords


	def render_map(self, level, show_spawns=False):
		spawns = []
		rune_spots = []

		for line in maps.LEVELS[level]:
			for obj in range(len(line)):
				crds = (obj*MAP_COORD_SHIFT[0], maps.LEVELS[level].index(line)*MAP_COORD_SHIFT[1])
				if line[obj] == maps.WALL:
					self.map_objects.append(objects.MapObject(images.get_wall(), crds, destroy_bullets=True))
				elif line[obj] == maps.RIVER:
					self.map_objects.append(objects.MapObject(images.get_river(), crds))
				elif line[obj] == maps.GRASS:
					self.grass.append(objects.Grass(crds))
				elif line[obj] == maps.SPAWN:
					if show_spawns:
						self.map_objects.append(objects.MapObject(images.get_spawn(), crds))
					spawns.append(crds)
				elif line[obj] == maps.RUNE:
					rune_spots.append(crds)


		return {'spawns':spawns, 'rune_spots':rune_spots}


	def start_battle(self):
		self.init_game_objects()
		self.game_status = 1
		self.score = 0

		return self.render_map(self.level)['spawns']


	def stop_battle(self):
		self.game_status = 0
		self.additional_objects = []
		self.init_optimization()


	def load_ammunition(self):
		self.ammunition = AMMUNITION_SIZE
		self.ammunition_string = str(AMMUNITION_SIZE)


	def update_ui(self):
		if type(self.ammunition) != type(1):
			time_diff = (datetime.now() - self.ammunition).total_seconds()
			if time_diff >= AMMUNITION_RELOAD_SPEED:
				self.load_ammunition()
			else:
				self.ammunition_string = '{:.1f}'.format(AMMUNITION_RELOAD_SPEED - time_diff)
		else:
			self.ammunition_string = str(self.ammunition)

		if self.player.boost:
			if self.active_runes[BOOST_RUNE_NAME] != False:
				self.boost_bar = pygame.transform.scale(self.boost_bar, (BOOST_BAR_SIZE[0], 
								BOOST_BAR_SIZE[1] * max(0.1, (RUNES_CONFIG['activity_times'][BOOST_RUNE_NAME] - (datetime.now() - self.active_runes[BOOST_RUNE_NAME]).total_seconds()) / RUNES_CONFIG['activity_times'][BOOST_RUNE_NAME])))
			else:
				self.boost_bar = pygame.transform.scale(self.boost_bar, (BOOST_BAR_SIZE[0], 
								BOOST_BAR_SIZE[1] * max(0.1, (BOOST_DURATION - (datetime.now() - self.player.boost_timer).total_seconds()) / BOOST_DURATION)))
		else:
			self.boost_bar = pygame.transform.scale(self.boost_bar, (BOOST_BAR_SIZE[0], 
								BOOST_BAR_SIZE[1] * min(1.0, max(0.1, (datetime.now() - self.player.boost_timer).total_seconds() / BOOST_RECOVERY_DURATION))))


	def set_up_runes(self):
		for i in range(len(self.runes)):
			if 'rect' not in self.runes[i] or 'image' not in self.runes[i]:
				self.runes[i]['image'] = images.get_runes()[self.runes[i]['rune']]['state']
				self.runes[i]['rect'] = self.runes[i]['image'].get_rect()
				self.runes[i]['rect'].x = self.runes[i]['coords'][0]
				self.runes[i]['rect'].y = self.runes[i]['coords'][1]


	def update_active_runes(self):
		for rune in self.active_runes:
			if self.active_runes[rune] != False and (datetime.now() - self.active_runes[rune]).total_seconds() > RUNES_CONFIG['activity_times'][rune]:
				self.active_runes[rune] = False
				self.deactivate_rune(rune)


	def respawn_player(self, position, rotation):
		self.player = objects.Tank(True, position, rotation)
		self.player_status = 'default'
		self.player.set_immunity()
		self.load_ammunition()
		self.active_runes = {i:False for i in RUNES_CONFIG['runes']}


	def activate_rune(self, rune:str):
		self.active_runes[rune] = datetime.now()
		self.change_player_state_on_rune(rune = rune, ch = True)


	def deactivate_rune(self, rune:str):
		self.change_player_state_on_rune(rune = rune, ch = False)


	def change_player_state_on_rune(self, rune:str, ch:bool):
		if rune == BOOST_RUNE_NAME:
			self.player.boost = ch
		elif rune == IMMUNITY_RUNE_NAME:
			self.player.immunity = ch


	def update_battle(self):
		self.player.shoot_iteration += 1
		self.player.general_update(self.active_runes)

		self.update_active_runes()

		self.update_ui()


	def shoot(self, tank):
		if tank.shoot_iteration < tank.shoot_speed:
			return

		if tank == self.player:
			self.ammunition -= 1

		if tank.rotation == 'forward':
			self.bullets.append(objects.Bullet(tank.rotation, (tank.rect.center[0] - 4*AVERAGE_MULTIPLYER, tank.rect.y - 8*AVERAGE_MULTIPLYER), shooter=tank))
		elif tank.rotation == 'back':
			self.bullets.append(objects.Bullet(tank.rotation, (tank.rect.center[0] - 4*AVERAGE_MULTIPLYER, tank.rect.y + 15*AVERAGE_MULTIPLYER), shooter=tank))
		elif tank.rotation == 'right':
			self.bullets.append(objects.Bullet(tank.rotation, (tank.rect.x + 15*AVERAGE_MULTIPLYER, tank.rect.center[1] - 4*AVERAGE_MULTIPLYER), shooter=tank))
		elif tank.rotation == 'left':
			self.bullets.append(objects.Bullet(tank.rotation, (tank.rect.x - 8*AVERAGE_MULTIPLYER, tank.rect.center[1] - 4*AVERAGE_MULTIPLYER), shooter=tank))

		tank.shouted = True
		tank.shoot_iteration = 0


	def go_on_reload(self):
		if type(self.ammunition) == type(1):
			if self.ammunition != AMMUNITION_SIZE:
				self.ammunition = datetime.now()


	def player_ready_to_shoot(self):
		if type(self.ammunition) == type(1):
			if self.ammunition > 0:
				return True
			self.go_on_reload()
		return False


	def change_nickname(self, new_nick):
		self.nickname_string = new_nick[:12:]
		f = open(CONFIG_FILE, 'r')
		data = json.load(f)
		f.close()
		data['NICKNAME'] = new_nick
		f = open(CONFIG_FILE, 'w')
		json.dump(data, f)
		f.close()

#	def process_object_animation(self, obj, imgs, iteration):
#		pass
