import os
import sys
import ssl
import time
import json
import utils
import socket
import pygame
import images
import platform
import traceback
import threading
import GameFunctions

from constants import *
from datetime import datetime
from crash_logging import crash_log
from scripts import objects, maps, blit, network_utils as ntwu

pygame.init()
pygame.font.init()


class NetworkHandler(): # run = NetworkHandler.start()
	def __init__(self):
		#threading.Thread.__init__(self, daemon=True)
		self.server = (SERVER_IP, SERVER_PORT)
		self.data_to_send = None
		self.recieved_data = []
		self.session_id = None
		self.player_data = None
		self.other_players_data = None

		self.server_update_time = 1 / TICK_RATE

	def run(self):
		while True:
			self.update()
			time.sleep(self.server_update_time)


	def update(self):
		if self.data_to_send != None:
			self.send_information(self.data_to_send)
			self.data_to_send = None
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





class Engine:
	def __init__(self, gf, settings_set):

		self.network = settings_set['network']
		self.player = settings_set['player']
		if self.network:
			self.network_handler = settings_set['network_handler']

			connneciton_result = self.network_handler.stable_connection()

			print(connneciton_result[1])
			if not connneciton_result[0]:
				self.quit()
			#self.network_handler.start()

		if settings_set['screen']:
			resolution = [WIDTH, HEIGHT]
			if 'WIDTH' in settings_set['screen']:
				resolution[0] == settings_set['screen']['WIDTH']
			if 'HEIGHT' in settings_set['screen']:
				resolution[1] == settings_set['screen']['HEIGHT']

			self.screen = pygame.display.set_mode(tuple(resolution))
			pygame.display.set_caption(settings_set['screen']['caption'])

			self.init_fonts()
		else:
			self.screen = pygame.display.set_mode((75, 75))
			pygame.display.set_caption('physics processing display')

		self.clock = pygame.time.Clock()
		self.iterations = 0 # Game iterations

		#self.positions = [(0, 0), (0, 0)]
		self.rotations = ['forward']*10
		self.server_update_timer = datetime.now()

	def init_fonts(self):
		if platform.system() == 'Linux':
			self.info_font = pygame.font.SysFont(SYS_FONT, INFO_FONT_SIZE)
			self.nickname_font = pygame.font.SysFont(SYS_FONT, NICK_FONT_SIZE)
			self.score_font = pygame.font.SysFont(SYS_FONT, SCORE_FONT_SIZE)
			self.ammunition_font = pygame.font.SysFont(SYS_FONT, AMMUNITION_FONT_SIZE)
		else:
			self.info_font = pygame.font.Font(GAME_FONT, INFO_FONT_SIZE)
			self.nickname_font = pygame.font.Font(GAME_FONT, NICK_FONT_SIZE)
			self.score_font = pygame.font.Font(GAME_FONT, SCORE_FONT_SIZE)
			self.ammunition_font = pygame.font.Font(GAME_FONT, AMMUNITION_FONT_SIZE)
		self.score_font_colors = [(180, 25, 25), (25, 180, 25), (25, 25, 180),]*3

	def start_battle(self, gf, battle_settings):

		if 'level' not in battle_settings:
			print(battle_settings)
			return

		gf.level = battle_settings['level']
		self.add_score_to_killer = None
		self.positions = gf.start_battle()

		if self.network:
			self.session_id = battle_settings['session_id']

			self.spawn_index = battle_settings['spawn_index']
		if self.player:
			gf.player = objects.Tank(True, self.positions[self.spawn_index], self.rotations[self.spawn_index])
			#print(gf.nickname_string)
			gf.nickname = self.nickname_font.render(gf.nickname_string, False, (255, 255, 255))

		#self.player_data = {"x":gf.player.rect.x, "y":gf.player.rect.y, "rotation":gf.player.rotation, "status":gf.player_status}


	def start_observing(self, gf, connection_info):
		self.session_id = connection_info['session_id']


	def main(self, gf):
		self.screen.fill((0, 0, 0))
		while True:
			self.clock.tick(FPS)
			self.game_loop(gf)


	def game_loop(self, gf):
		self.update(gf)

		self.blit_objects(gf)

		self.iterations += 1
		pygame.display.update()
		pygame.event.pump()


	def update(self, gf):

		#if utils.event_handling(gf) == 'quit':
		#	self.quit()

		if gf.game_status == 0 and self.network:
			res = gf.main_menu_update(socket = self.network_handler.socket, get_information = self.network_handler.get_information)

			if res == 'leave':
				self.quit()
			elif 'observing' in str(res):
				self.start_observing(gf, res)
				self.network_handler.session_id = gf.session_id
			elif res != None:
				self.start_battle(gf, res)
				self.network_handler.session_id = gf.session_id

		if gf.game_status == 1:
			if gf.player == None:
				death_time = (datetime.now() - gf.death_timer).total_seconds()
				if death_time >= DEATH_DURATION:
					gf.respawn_player(position=self.positions[self.spawn_index], rotation=self.rotations[self.spawn_index])
				else:
					gf.ammunition_string = '{:.1f}'.format(DEATH_DURATION - death_time)
			else:
				gf.update_battle()
				if self.player:
					self.player_data = {"x":gf.player.rect.x, "y":gf.player.rect.y, "rotation":gf.player.rotation, "status":gf.player_status, "shouted":int(gf.player.shouted),
										"nickname":gf.nickname_string, "spawn_index":self.spawn_index, 'alive':int(gf.player.alive),
										'statuses':{"boost":int(gf.player.boost), "immunity":int(gf.player.immunity)}}
					self.update_player(gf)


			if self.iterations % FPS*5 == 0:
				gf.players = {}
			if self.player:
				if self.add_score_to_killer != None:
					self.player_data['killer'] = self.add_score_to_killer
					self.add_score_to_killer = None
				if gf.player != None:
					gf.player.shouted = False
				self.network_handler.player_data = self.player_data

			self.struct_players_info(gf, self.network_handler.other_players_data)
			if self.player:
				self.scores.insert(0, (self.score_font.render(f'{gf.score}', False, (255, 255, 255)), self.info_font.render(f'{gf.nickname_string}', False, (255, 255, 255)), gf.nickname_string))


			self.update_bullets(gf)

			rm_lst = []

			for player in gf.players: # gf.players is dict
				if gf.players[player] != None:
					gf.players[player].show_nickname = True
					for obj in gf.grass:
						if obj.rect.colliderect(gf.players[player].rect):
							gf.players[player].show_nickname = False
							break

					if gf.players[player].process_death():
						rm_lst.append(player)

			for obj in rm_lst:
				del gf.players[obj]
		elif gf.game_status == 2:
			pass
		elif gf.game_status == 3:

			self.update_bullets(gf)

			if self.it_is_time_to_update_server():
				info = {'session_id':self.session_id, 'observing':1}
				self.send_information(info)
				players_info = self.get_information()
				if self.message_has_an_error(players_info):
					print('Session does not exist yet or anymore')
					self.exit_map(gf)
					return
				self.struct_players_info(gf, players_info)
				self.reset_server_update_timer()

			rm_lst = []

			for player in gf.players:
				if gf.players[player].process_death():
					rm_lst.append(player)

			for obj in rm_lst:
				del gf.players[obj]


		if self.iterations >= 3628800: # 3628800 = !10
			self.iterations = 0


	def update_player(self, gf):
		gf.player.show_nickname = True
		for obj in gf.grass:
			if obj.rect.colliderect(gf.player.rect) or gf.reveal_grass:
				obj.image = obj.images['transparent']
				gf.player.show_nickname = False
			else:
				obj.image = obj.images['filled']

		for rune in gf.runes: # gf.runes is list
			if rune['rect'].colliderect(gf.player.rect):
				self.player_data['rune_collected'] = rune['id']

		if gf.player.process_death():
			gf.player = None
			gf.death_timer = datetime.now()

	def message_has_an_error(self, message):
		return '_error' in message


	def reset_server_update_timer(self):
		self.server_update_timer = datetime.now()


	def struct_players_info(self, gf, players_info):
		self.scores = []

		if type(players_info) != dict:
			return

		try:
			if self.player:
				self.struct_self_info(gf, players_info['player_info'])

			players_info = players_info['other_players']

			for player in players_info:
				if type(player) == type(0):
					gf.score = player
					continue
				addr = player['address']
				x = player['x']
				y = player['y']
				rot = player['rotation']
				status = player['status']
				shouted = player['shouted']
				nickname = player['nickname']
				spawn_index = player['spawn_index']
				score = str(player['score'])
				alive = player['alive']
				boost = player['statuses']['boost']
				immunity = player['statuses']['immunity']

				self.scores.append((self.score_font.render(score, False, self.score_font_colors[players_info.index(player)]), 
									self.info_font.render(nickname, False, (255, 255, 255)), nickname))

				if addr in gf.players:
					gf.players[addr].update(x, y, rot, score, alive=bool(alive), boost=bool(boost), immunity=bool(immunity))
				elif alive:
					gf.players[addr] = objects.Tank(False, (x, y), rot, shoot_speed=TANK_SHOOT_SPEED//2, spawn_index=spawn_index)
					gf.players[addr].nickname = self.nickname_font.render(nickname, False, (255, 255, 255))
					gf.players[addr].show_nickname = True

				if shouted:
					gf.shoot(gf.players[addr])
		except Exception as e:
			print(e)
			#elif status == 'dead':
			#	gf.players[addr].alive = False


	def struct_self_info(self, gf, info):
		for key in info:
			if key == 'runes':
				gf.set_up_runes(info[key])
			elif key == 'rune_collected':
				gf.activate_rune(rune=info[key]) # string


	def update_bullets(self, gf):
		rm_lst = []
		for bullet in gf.bullets:
			bullet.update()
			for obj in gf.map_objects:
				if obj.destroy_bullets:
					if bullet.rect.colliderect(obj.rect) or bullet.rect.x < 0 or bullet.rect.y < 0 or bullet.rect.y > HEIGHT or bullet.rect.x > WIDTH:
						rm_lst.append(bullet)
						break


			if gf.game_status == 1 and gf.player != None and bullet.rect.colliderect(gf.player.rect):
				if gf.player.alive and not gf.player.immunity:
					gf.player.alive = False
					if bullet.shooter.spawn_index != None:
						self.add_score_to_killer = bullet.shooter.spawn_index
					else:
						self.add_score_to_killer = self.spawn_index
				rm_lst.append(bullet)

			for player in gf.players:
				if bullet.rect.colliderect(gf.players[player].rect):
					#gf.players[player].alive = False
					rm_lst.append(bullet)
					break

		for bullet in rm_lst:
			if bullet in gf.bullets:
				gf.bullets.remove(bullet)



	def blit_interface(self, gf):
		ammunation = self.ammunition_font.render(gf.ammunition_string, False, (255, 75, 75))
		boost_bar_position = (1, HEIGHT - gf.boost_bar.get_height())
		ammunation_position = (BOOST_BAR_SIZE[0] + 2*AVERAGE_MULTIPLYER, HEIGHT - AMMUNITION_FONT_SIZE)
		self.screen.blit(ammunation, ammunation_position)
		self.screen.blit(gf.boost_bar_background, (1, HEIGHT - BOOST_BAR_SIZE[1]))
		self.screen.blit(gf.boost_bar, boost_bar_position)


	def blit_objects(self, gf):
		self.screen.fill((0, 0, 0))
		if gf.game_status != 0:
			blit.blit_map(screen=self.screen, gf=gf)

			if gf.game_status in [1, 3]:
				if gf.game_status == 1:
					blit.blit_player(screen=self.screen, gf=gf)
					self.blit_interface(gf)
				blit.blit_other_players(screen=self.screen, gf=gf)
				blit.blit_bullets(screen=self.screen, gf=gf)
				blit.blit_runes(screen=self.screen, gf=gf)

			blit.blit_grass(screen=self.screen, gf=gf)
			#blit.blit_text()

			if gf.game_status in [1, 3]:
				blit.blit_scores(screen=self.screen, scores=self.scores)

		blit.blit_additional_objects(screen=self.screen, gf=gf)

	def exit_map(self, gf):
		if gf.game_status in [1, 2, 3]:
			gf.stop_battle()

	def quit(self):
		self.network_handler.disconnect()
		pygame.quit()
		sys.exit()


def run(gf, settings_set): #setting set could be found in additional_engine_settings
	print(GAME_NAME, GAME_VERSION, end='\n\n')

	try:
		return Engine(gf, settings_set)
	except Exception as e:
		if e != SystemExit:
			print(traceback.format_exc())
			input('\n\n PRESS ENTER TO EXIT GAME CRASH: ')

