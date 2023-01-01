import os
import sys
import time
import json
import utils
import pygame
import images
import platform
import traceback
import GameFunctions

from constants import *
from datetime import datetime
from crash_logging import crash_log
from scripts import objects, maps, blit, network_utils as ntwu

pygame.init()
pygame.font.init()


class Engine:
	def __init__(self, gf, settings_set):

		self.settings = settings_set

		self.network = settings_set['network']
		self.player = settings_set['player']
		self.screen_usage = bool(settings_set['screen'])

		#self.positions = [(0, 0), (0, 0)]
		self.rotations = ['forward']*10
		self.init_fonts()
		self.clock = pygame.time.Clock()
		self.iterations = 0 # Game iterations

		self.server_update_timer = datetime.now()

		if self.network:
			self.network_handler = settings_set['network_handler']

			connneciton_result = self.network_handler.stable_connection()

			print(connneciton_result[1])
			if not connneciton_result[0]:
				self.quit()
			self.network_handler.start()
			self.player_id = None
		else:
			self.localgame = settings_set['localgame']
			self.player_id = utils.gen_random_shake(length=6)

			self.start_battle(gf, battle_settings={'level':settings_set['level'], 'spawn_index':self.localgame.add_player(player_id=self.player_id)})

		if settings_set['screen']:
			resolution = [WIDTH, HEIGHT]
			if 'WIDTH' in settings_set['screen']:
				resolution[0] == settings_set['screen']['WIDTH']
			if 'HEIGHT' in settings_set['screen']:
				resolution[1] == settings_set['screen']['HEIGHT']

			self.screen = pygame.display.set_mode(tuple(resolution))
			pygame.display.set_caption(settings_set['screen']['caption'])
		else:
			self.screen = pygame.display.set_mode((215, 215))
			pygame.display.set_caption('physics processing display')


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

		if self.player:
			self.spawn_index = battle_settings['spawn_index']
			gf.player = objects.Tank(True, self.positions[self.spawn_index], self.rotations[self.spawn_index], ID=self.player_id)
			#print(gf.nickname_string)
			gf.nickname = self.nickname_font.render(gf.nickname_string, False, (255, 255, 255))


	def start_observing(self, gf, connection_info):
		self.session_id = connection_info['session_id']


	def main(self, gf):
		self.screen.fill((0, 0, 0))
		while True:
			self.clock.tick(FPS)
			self.game_loop(gf)


	def game_loop(self, gf):
		self.update(gf)

		if self.screen_usage:
			self.blit_objects(gf)
		else:
			self.screen.fill((0, 0, 0))

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

		if gf.game_status != 0:
			if gf.game_status == 1:
				if gf.player == None and self.player:
					death_time = (datetime.now() - gf.death_timer).total_seconds()
					if death_time >= DEATH_DURATION:
						gf.respawn_player(position=self.positions[self.spawn_index], rotation=self.rotations[self.spawn_index], ID=self.player_id)
					else:
						gf.ammunition_string = '{:.1f}'.format(DEATH_DURATION - death_time)
				else:
					if self.player:
						gf.update_battle()
						self.player_data = {"x":gf.player.rect.x, "y":gf.player.rect.y, "rotation":gf.player.rotation,
											"status":gf.player.status, "shouted":int(gf.player.shouted),
											"nickname":gf.nickname_string, "spawn_index":self.spawn_index, 'alive':int(gf.player.alive),
											'statuses':{"boost":int(gf.player.boost), "immunity":int(gf.player.immunity)}}
						self.update_player(gf)
						if not self.network:
							self.localgame.update_players(gf, players={player:gf.players[player] for player in gf.players if gf.players[player].id != self.player_id})


			if self.iterations % FPS*5 == 0 and self.network:
				gf.players = {}

			if self.player and gf.game_status == 1:
				if self.add_score_to_killer != None:
					self.player_data['killer'] = self.add_score_to_killer
					self.add_score_to_killer = None
				if gf.player != None:
					gf.player.shouted = False

				if self.network:
					self.network_handler.player_data = self.player_data
				else:
					self.localgame.players[self.player_id] = self.player_data

			if gf.game_status == 3:
				self.network_handler.send(key='other_players_data', data = {'session_id':self.network_handler.session_id, 'observing':1})
				self.network_handler.other_players_data = self.network_handler.recieved_data['other_players_data']

			if self.network:
				self.struct_players_info(gf, self.network_handler.other_players_data)
			else:
				self.struct_players_info(gf, [self.localgame.players[player] for player in self.localgame.players if player != self.player_id])

			if self.player and gf.game_status == 1 and self.screen_usage:
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
						if self.network:
							rm_lst.append(player)
						else:
							gf.players[player].respawn()

			for obj in rm_lst:
				del gf.players[obj]

		if self.iterations >= 3628800: # 3628800 = !10
			self.iterations = 0


	def update_player(self, gf):
		if not self.network:
			self.player_data['address'] = self.player_id
			self.player_data['score'] = self.localgame.scores[self.player_id]
			gf.score = self.player_data['score']
			self.player_data['id'] = self.player_id

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
			if self.network:
				gf.player = None
				gf.death_timer = datetime.now()
			else:
				gf.player.respawn()

	def message_has_an_error(self, message):
		return '_error' in message


	def reset_server_update_timer(self):
		self.server_update_timer = datetime.now()


	def struct_players_info(self, gf, players_info):
		self.scores = []

		if type(players_info) not in [dict, list]:
			return

		try:

			if type(players_info) == dict:
				if self.player and gf.player != None:
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


				if self.screen_usage:
					self.scores.append((self.score_font.render(score, False, self.score_font_colors[players_info.index(player)]), 
									self.info_font.render(nickname, False, (255, 255, 255)), nickname))

				if addr in gf.players:
					gf.players[addr].update(x, y, rot, score, alive=bool(alive), boost=bool(boost), immunity=bool(immunity))
				elif alive:
					if self.network:
						player['id'] = None
					gf.players[addr] = objects.Tank(False, (x, y), rot, shoot_speed=TANK_SHOOT_SPEED//2, spawn_index=spawn_index, ID=player['id'])
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
					if not self.network:
						gf.players[player].alive = False
					if bullet.shooter != None:
						if bullet.shooter == gf.player or bullet.shooter in gf.players:
							bullet.shooter.killed_someone = True
							if not self.network:
								self.localgame.scores[bullet.shooter.id] += 1
						elif gf.player != None:
							gf.player.killed_someone = True
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
		if self.network:
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

