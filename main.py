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
import GameFunctions

from constants import *
from scripts import objects, maps
from datetime import datetime
from crash_logging import crash_log

pygame.init()
pygame.font.init()

class Main:
	def __init__(self, gf):
		self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
		pygame.display.set_caption(GAME_NAME)

		self.init_fonts()

		self.clock = pygame.time.Clock()
		self.iterations = 0 # Game iterations

		#self.positions = [(0, 0), (0, 0)]
		self.rotations = ['forward']*10


		self.server = (SERVER_IP, SERVER_PORT) # from constants
		self.connect()

		while True:
			self.s.send(utils.prepare_object_to_sending('confirmation_request'))
			command = self.get_information(parse=False)
			exec(command)
			self.s.send(utils.prepare_object_to_sending(f'confirmation_response {self.confirmation_result}'))
			if self.get_information(parse=False) == 'success':
				print('Files confimation successfull')
				break
			else:
				self.disconnect()
				input('Files confimation failed; check wether game is up to date; press enter to quit')
				self.quit()


		#sessions_info = self.get_information().split(' ')

		#if connection_info:

		self.server_update_time = 1 / TICK_RATE
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

		#self.player_data = {"x":gf.player.rect.x, "y":gf.player.rect.y, "rotation":gf.player.rotation, "status":gf.player_status}


	def start_observing(self, gf, connection_info):
		self.session_id = connection_info['session_id']


	def main(self, gf):
		#gf.start_battle()
		self.screen.fill((0, 0, 0))
		while True:

			self.update(gf)

			self.blit_objects(gf)

			self.clock.tick(FPS)
			self.iterations += 1
			pygame.display.update()
			pygame.event.pump()


	def update(self, gf):

		self.event_update()

		if gf.game_status == 0:
			res = gf.main_menu_update(socket = self.s, get_information = self.get_information)

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
					gf.player = objects.Tank(True, self.positions[self.spawn_index], self.rotations[self.spawn_index])
					gf.player_status = 'default'
					gf.immunity_timer = datetime.now()
					gf.load_ammunition()
				else:
					gf.ammunition_string = '{:.1f}'.format(DEATH_DURATION - death_time)
			else:
				gf.update_battle()
				self.player_data = {"x":gf.player.rect.x, "y":gf.player.rect.y, "rotation":gf.player.rotation, "status":gf.player_status, "shouted":int(gf.player.shouted),
									"nickname":gf.nickname_string, "spawn_index":self.spawn_index, 'alive':int(gf.player.alive)}


			if self.it_is_time_to_update_server():
				if self.iterations % FPS*5 == 0:
					gf.players = {}
				if self.add_score_to_killer != None:
					self.player_data['killer'] = self.add_score_to_killer
					self.add_score_to_killer = None
				self.send_player_data()
				if gf.player != None:
					gf.player.shouted = False
				players_info = self.get_information()

				self.struct_players_info(gf, players_info)

				self.reset_server_update_timer()
				self.scores.insert(0, (self.score_font.render(f'{gf.score}', False, (255, 255, 255)), self.info_font.render(f'{gf.nickname_string}', False, (255, 255, 255)),
									gf.nickname_string))

			self.update_bullets(gf)


			if gf.player != None:
				gf.player.show_nickname = True
				for obj in gf.grass:
					if obj.rect.colliderect(gf.player.rect):
						obj.image = obj.images['transparent']
						gf.player.show_nickname = False
					else:
						obj.image = obj.images['filled']

				if gf.player.process_death():
					gf.player = None
					gf.death_timer = datetime.now()

			rm_lst = []

			for player in gf.players:
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

			for obj in gf.grass:
				for player in gf.players:
					if gf.players[player] != None:
						if obj.rect.colliderect(gf.players[player].rect):
							obj.image = obj.images['transparent']
							break
						else:
							obj.image = obj.images['filled']

			for player in gf.players:
				if gf.players[player].process_death():
					rm_lst.append(player)

			for obj in rm_lst:
				del gf.players[obj]


		if self.iterations >= 3628800: # 3628800 = !10
			self.iterations = 0


	def message_has_an_error(self, message):
		return '_error' in message


	def it_is_time_to_update_server(self):
		return (datetime.now() - self.server_update_timer).total_seconds() >= self.server_update_time


	def reset_server_update_timer(self):
		self.server_update_timer = datetime.now()


	def struct_players_info(self, gf, players_info):
		self.scores = []

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

			self.scores.append((self.score_font.render(score, False, self.score_font_colors[players_info.index(player)]), 
								self.info_font.render(nickname, False, (255, 255, 255)), nickname))

			if addr in gf.players:
				gf.players[addr].update(x, y, rot, score, alive=bool(alive))
			elif alive:
				gf.players[addr] = objects.Tank(False, (x, y), rot, shoot_speed=TANK_SHOOT_SPEED//2, spawn_index=spawn_index)
				gf.players[addr].nickname = self.nickname_font.render(nickname, False, (255, 255, 255))
				gf.players[addr].show_nickname = True

			if shouted:
				gf.shoot(gf.players[addr])
			#elif status == 'dead':
			#	gf.players[addr].alive = False


	def update_bullets(self, gf):
		rm_lst = []
		for bullet in gf.bullets:
			bullet.update()
			for obj in gf.map_objects:
				if obj.destroy_bullets:
					if bullet.rect.colliderect(obj.rect) or bullet.rect.x < 0 or bullet.rect.y < 0 or bullet.rect.y > HEIGHT or bullet.rect.x > WIDTH:
						rm_lst.append(bullet)
						break


			if gf.game_status == 1 and gf.player != None and bullet.rect.colliderect(gf.player.rect) and gf.immunity_timer == None:
				if gf.player.alive:
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


	def blit_grass(self, gf):
		for obj in gf.grass:
			self.screen.blit(obj.image, obj.rect)


	def blit_map(self, gf, preview=[]):
		for obj in gf.map_objects:
			self.screen.blit(obj.image, obj.rect)


	def blit_scores(self):
		for i in range(len(self.scores)):
			score_lenth_unit = (SCORE_FONT_SIZE)*(len(self.scores)*1.25 - 1)
			score_coords = (WIDTH // 2 - (score_lenth_unit // 2) - SCORE_FONT_SIZE*.5 + (SCORE_FONT_SIZE + SCORE_FONT_SIZE*0.85)*i, AVERAGE_MULTIPLYER)
			nick_coords = (score_coords[0]+(SCORE_FONT_SIZE - (NICK_FONT_SIZE*len(self.scores[i][2])))//4, score_coords[1] + SCORE_FONT_SIZE + AVERAGE_MULTIPLYER)
			# 
			self.screen.blit(self.scores[i][0], score_coords)
			self.screen.blit(self.scores[i][1], nick_coords)


	def blit_other_players(self, gf):
		for player in gf.players:
			self.screen.blit(gf.players[player].image, gf.players[player].rect)
			if gf.players[player].show_nickname:
				self.screen.blit(gf.players[player].nickname, (gf.players[player].rect.x, gf.players[player].rect.y - 8*AVERAGE_MULTIPLYER))


	def blit_player(self, gf):
		try:
			self.screen.blit(gf.player.image, gf.player.rect)
			if gf.player.show_nickname:
				self.screen.blit(gf.nickname, (gf.player.rect.x, gf.player.rect.y - 8*AVERAGE_MULTIPLYER))
		except:
			pass
		ammunation = self.ammunition_font.render(gf.ammunition_string, False, (255, 75, 75))
		ammunation_position = (0, HEIGHT - AMMUNITION_FONT_SIZE)
		self.screen.blit(ammunation, ammunation_position)


	def blit_bullets(self, gf):
		for bullet in gf.bullets:
			self.screen.blit(bullet.image, bullet.rect)


	def blit_objects(self, gf):
		self.screen.fill((0, 0, 0))
		if gf.game_status != 0:
			self.blit_map(gf)

			if gf.game_status in [1, 3]:
				if gf.game_status == 1:
					self.blit_player(gf)
				self.blit_other_players(gf)
				self.blit_bullets(gf)

			self.blit_grass(gf)
			#self.blit_text()

			if gf.game_status in [1, 3]:
				self.blit_scores()

		for obj in gf.additional_objects:
			self.screen.blit(obj.image, obj.rect)


	def event_update(self):
		pressed_keys = pygame.key.get_pressed()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.quit()
			elif event.type == pygame.MOUSEBUTTONDOWN:
				mos_pos = pygame.mouse.get_pos()
				for obj in gf.additional_objects:
					if obj.__class__.__name__ == 'Button' and obj.rect.collidepoint(mos_pos):
						obj.action(gf = gf, main = self)
						break
			#elif event.type == pygame.KEYDOWN:
				#if event.key == pygame.K_t and gf.player != None:
				#	gf.player.alive = False

		if gf.game_status == 1 and gf.player != None and gf.player.alive:# and self.iterations % MOVEMENT_TICKS == 0:
			gf.player.boost = pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]

			if pressed_keys[pygame.K_UP]:
				gf.player.move(gf.map_objects, 'forward')
			elif pressed_keys[pygame.K_DOWN]:
				gf.player.move(gf.map_objects, 'back')
			elif pressed_keys[pygame.K_RIGHT]:
				gf.player.move(gf.map_objects, 'right')
			elif pressed_keys[pygame.K_LEFT]:
				gf.player.move(gf.map_objects, 'left')

			if pressed_keys[pygame.K_SPACE]:
				if gf.player_ready_to_shoot():
					gf.shoot(gf.player)
			if pressed_keys[pygame.K_r]:
				gf.go_on_reload()


	def get_information(self=None, parse=True):
		info = self.s.recv(1024).decode(ENCODING)
		if parse and ('[' in info or '{' in info):
			return json.loads(info)
		return info

	def send_information(self, info):
		self.s.send(utils.prepare_object_to_sending(info))

	def send_player_data(self):
		info = {'session_id':self.session_id, 'player_data':self.player_data}
		self.send_information(info)

	def connect(self):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.s = ssl.wrap_socket(self.s, certfile="tbc_cert.pem", keyfile="tbc_key.pem")
		self.s.connect(self.server)

	def disconnect(self):
		if self.s.fileno() != -1:
			self.s.shutdown(socket.SHUT_RDWR)
			self.s.close()

	def exit_map(self, gf):
		if gf.game_status in [1, 2, 3]:
			gf.stop_battle()

	def quit(self):
		self.disconnect()
		pygame.quit()
		sys.exit()




if __name__ == '__main__':
	print(GAME_NAME, GAME_VERSION)

	gf = GameFunctions.GameFunctions()

	try:
		Main(gf).main(gf)
	except Exception as e:
		if e != SystemExit:
			print(traceback.format_exc())
			input('\n\n PRESS ENTER TO EXIT GAME CRASH: ')
