import os
import sys
import ssl
import time
import utils
import socket
import pygame
import images
import random
import hashlib
import platform
import traceback
import threading
import GameFunctions

from constants import *
from datetime import datetime
from crash_logging import crash_log
from scripts import objects, maps, blit
from network import Client, prepare_object_to_sending

pygame.init()
pygame.font.init()

class Main(Client):
	def __init__(self, gf):
		self.player_ident = hashlib.sha256(f'{random.randint(1, 1<<256)}'.encode()).hexdigest()

		self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
		pygame.display.set_caption(GAME_NAME)

		self.init_fonts()
		utils.init_devices()

		self.clock = pygame.time.Clock()
		self.iterations = 0 # Game iterations

		#self.positions = [(0, 0), (0, 0)]
		self.rotations = ['forward']*10


		#self.server = (SERVER_IP, SERVER_PORT) # from constants
		super().__init__()


		#sessions_info = self.get_information().split(' ')

		#if connection_info:

		self.server_update_time = 1 / TICK_RATE
		self.server_update_timer = datetime.now()
		self.scores = []


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


	def start_battle(self, gf, connection_info):

		if 'level' not in connection_info:
			print(connection_info)
			return

		gf.level = connection_info['level']
		self.add_score_to_killer = None
		self.positions = gf.start_battle()
		self.session_id = connection_info['session_id']

		self.spawn_index = connection_info['spawn_index']
		gf.player = objects.Tank(True, self.positions[self.spawn_index], self.rotations[self.spawn_index])
		print(gf.nickname_string)
		gf.nickname = self.nickname_font.render(gf.nickname_string, False, (255, 255, 255))

		threading.Thread(target=self.server_updating_thread, args=(gf,), daemon=True).start()

		#self.player_data = {"x":gf.player.rect.x, "y":gf.player.rect.y, "rotation":gf.player.rotation, "status":gf.player_status}


	def start_observing(self, gf, connection_info):
		self.session_id = connection_info['session_id']
		threading.Thread(target=self.server_updating_thread, args=(gf,), daemon=True).start()


	def it_is_time_to_update_server(self):
		return (datetime.now() - self.server_update_timer).total_seconds() >= self.server_update_time


	def main(self, gf):
		self.screen.fill((0, 0, 0))
		while True:

			self.update(gf)

			self.blit_objects(gf)

			self.clock.tick(FPS)
			self.iterations += 1
			pygame.display.update()
			pygame.event.pump()


	def server_updating_thread(self, gf):
		"""Run as thread"""

		server_update_time = 1 / TICK_RATE
		server_update_timer = datetime.now()

		def _it_is_time_to_update_server():
			return (datetime.now() - server_update_timer).total_seconds() >= server_update_time

		while gf.game_status == 1 or gf.game_status == 3:
			if _it_is_time_to_update_server():
				if gf.game_status == 1:
					if self.iterations % FPS*5 == 0:
						gf.players = {}
					if self.add_score_to_killer != None:
						self.player_data['killer'] = self.add_score_to_killer
						self.add_score_to_killer = None
					self.send_player_data()
					if gf.player != None:
						gf.player.shouted = {'state':0}
					players_info = self.get_information()

					self.struct_players_info(gf, players_info)

					self.scores.insert(0, (self.score_font.render(f'{gf.score}', False, (255, 255, 255)), self.info_font.render(f'{gf.nickname_string}', False, (255, 255, 255)),
										gf.nickname_string))
				elif gf.game_status == 3:
					info = {'session_id':self.session_id, 'observing':1}
					self.send_information(info)
					players_info = self.get_information()
					if self.message_has_an_error(players_info):
						print('Session does not exist yet or anymore')
						self.exit_map(gf)
						return
					self.struct_players_info(gf, players_info)

				server_update_timer = datetime.now()
			time.sleep(0.001)


	def update(self, gf):

		if utils.event_handling(gf) == 'quit':
			self.quit()

		if gf.game_status == 0:
			res = gf.main_menu_update(socket = self.socket, get_information = self.get_information)

			if res == 'leave':
				self.quit()
			elif 'observing' in str(res):
				self.start_observing(gf, res)
			elif res != None:
				self.start_battle(gf, res)

		if gf.game_status == 1:
			if gf.player == None:
				death_time = (datetime.now() - gf.death_timer).total_seconds()
				if death_time >= DEATH_DURATION:
					gf.respawn_player(position=self.positions[self.spawn_index], rotation=self.rotations[self.spawn_index])
				else:
					gf.ammunition_string = '{:.1f}'.format(DEATH_DURATION - death_time)
			else:
				gf.update_battle()
				self.player_data = {"x":gf.player.rect.x, "y":gf.player.rect.y, "rotation":gf.player.rotation, "status":gf.player_status, "shouted":gf.player.shouted,
									"nickname":gf.nickname_string, "spawn_index":self.spawn_index, 'alive':int(gf.player.alive),
									'statuses':{"boost":int(gf.player.boost), "immunity":int(gf.player.immunity)}, 'id':self.player_ident}
				self.update_player(gf)

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
		#if not gf.game_status == 3:
		self.struct_self_info(gf, players_info['player_info'])

		for shoot in set(players_info['shoots']) - set(gf.shoots):
			content = players_info['shoots'][shoot]
			if content['id'] in gf.players:
				gf.shoot(gf.players[content['id']], position=content['position'], rotation=content['rotation'])

		gf.shoots = players_info['shoots']


		players_info = players_info['other_players']


		for player in players_info:
			if type(player) == type(0):
				gf.score = player
				continue
			addr = player['id']
			x = player['x']
			y = player['y']
			rot = player['rotation']
			status = player['status']
			#shouted = player['shouted']
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

			#if shouted:
			#	gf.shoot(gf.players[addr])
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
					if gf.player.alive != False:
						gf.player.alive = False
						utils.player_death()
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
		self.disconnect()
		pygame.quit()
		sys.exit()




if __name__ == '__main__':
	print(GAME_NAME, GAME_VERSION, end='\n\n')

	gf = GameFunctions.GameFunctions()

	try:
		Main(gf).main(gf)
	except Exception as e:
		if e != SystemExit:
			print(traceback.format_exc())
			input('\n\n PRESS ENTER TO EXIT GAME CRASH: ')
