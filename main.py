import pygame, images, GameFunctions, sys, os, socket, time, json, utils
from constants import *
from scripts import objects, maps
from datetime import datetime

pygame.init()
pygame.font.init()


GAME_NAME = 'Turbo Batlle City'
GAME_VERSION = '1.0'

class Main:
	def __init__(self, gf):
		self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
		pygame.display.set_caption(GAME_NAME)

		self.clock = pygame.time.Clock()
		self.iterations = 0 # Game iterations

		#self.positions = [(0, 0), (0, 0)]
		self.rotations = ['forward']*10


		self.server = ('192.168.1.23', 25215) #192.168.0.181
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

		self.server_update_time = .03125 # 32 tick rate, .015625 - 64
		self.server_update_timer = datetime.now()

	def start_battle(self, gf, connection_info):

		gf.level = connection_info['level']
		self.positions = gf.start_battle()
		self.session_id = connection_info['session_id']

		self.player_idx = connection_info['player_idx']
		gf.player = objects.Tank(True, self.positions[self.player_idx], self.rotations[self.player_idx])

		self.player_data = {"x":gf.player.rect.x, "y":gf.player.rect.y, "rotation":gf.player.rotation, "status":gf.player_status}

	def main(self, gf):
		#gf.start_battle()
		while True:
			self.screen.fill((0, 0, 0))


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
			if res != None:
				if res == 'leave':
					self.quit()
				self.start_battle(gf, res)

		if gf.game_status == 1:
			gf.update_battle()
			self.player_data = {"x":gf.player.rect.x, "y":gf.player.rect.y, "rotation":gf.player.rotation, "status":gf.player_status, "shouted":int(gf.shouted)}

			rm_lst = []
			for bullet in gf.bullets:
				bullet.update()
				for obj in gf.map_objects:
					if obj.__class__.__name__ == 'Wall':
						if bullet.rect.colliderect(obj.rect) or bullet.rect.x < 0 or bullet.rect.y < 0 or bullet.rect.y > HEIGHT or bullet.rect.x > WIDTH:
							rm_lst.append(bullet)
							break

				if bullet.rect.colliderect(gf.player.rect):
					gf.player.alive = False
					rm_lst.append(bullet)

				for player in gf.players:
					if bullet.rect.colliderect(gf.players[player].rect):
						gf.players[player].alive = False
						rm_lst.append(bullet)
						break

			for bullet in rm_lst:
				gf.bullets.remove(bullet)

			if (datetime.now() - self.server_update_timer).total_seconds() >= self.server_update_time:
				self.send_information()
				gf.shouted = False
				#print('info sent')
				players_info = self.get_information()
				#print('info got')

				for player in players_info:
					addr = player['address']
					x = player['x']
					y = player['y']
					rot = player['rotation']
					status = player['status']
					shouted = player['shouted']

					if addr in gf.players:
						gf.players[addr].update(x, y, rot)
					else:
						gf.players[addr] = objects.Tank(False, (x, y), rot)

					if shouted:
						gf.shoot(gf.players[addr])
					elif status == 'dead':
						gf.players[addr].alive = False

				self.server_update_timer = datetime.now()

			if gf.player != None:
				for obj in gf.grass:
					if obj.rect.colliderect(gf.player.rect):
						obj.image = obj.images['transparent']
					else:
						obj.image = obj.images['filled']

			if gf.player != None and gf.player.alive == False:
				gf.player.death_animation_iteration += 1
				if gf.player.death_animation_iteration <= gf.player.death_animation_speed:
					gf.player.image = gf.player.death_images[0]
				elif gf.player.death_animation_iteration > gf.player.death_animation_speed * 2:
					gf.player = objects.Tank(True, self.positions[self.player_idx], self.rotations[self.player_idx])
					gf.player_status = 'default'
				else:
					gf.player.image = gf.player.death_images[1]

			rm_lst = []

			for player in gf.players:
				if gf.players[player] != None and gf.players[player].alive == False:
					gf.players[player].death_animation_iteration += 1
					if gf.players[player].death_animation_iteration <= gf.players[player].death_animation_speed:
						gf.players[player].image = gf.players[player].death_images[0]
					elif gf.players[player].death_animation_iteration > gf.players[player].death_animation_speed * 2:
						rm_lst.append(player)
					else:
						gf.players[player].image = gf.players[player].death_images[1]

			for obj in rm_lst:
				del gf.players[obj]

		#string = f"{self.player_idx} {gf.player.rect.x}-{gf.player.rect.y}:{gf.player.rotation} {len(gf.added_bullets)}"

		#for bullet in gf.added_bullets:
		#	string += f" {bullet.rect.x}-{bullet.rect.y}-{bullet.rotation}"

		#self.s.sendto(string.encode(ENCODING), self.server)

		if self.iterations == 3628800: # 3628800 = !10
			self.iterations = 0

	def blit_objects(self, gf):
		for obj in gf.additional_objects:
			self.screen.blit(obj.image, obj.rect)

		if gf.game_status == 1:
			try:
				self.screen.blit(gf.player.image, gf.player.rect)
			except: pass
			for player in gf.players:
				self.screen.blit(gf.players[player].image, gf.players[player].rect)

			for obj in gf.map_objects:
				self.screen.blit(obj.image, obj.rect)

			for bullet in gf.bullets:
				self.screen.blit(bullet.image, bullet.rect)

			for obj in gf.grass:
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
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_t and gf.player != None:
					gf.player.alive = False

		if gf.game_status == 1 and gf.player != None and gf.player.alive:
			if pressed_keys[pygame.K_UP]:
				gf.player.move(gf.map_objects, 'forward')
			elif pressed_keys[pygame.K_DOWN]:
				gf.player.move(gf.map_objects, 'back')
			elif pressed_keys[pygame.K_RIGHT]:
				gf.player.move(gf.map_objects, 'right')
			elif pressed_keys[pygame.K_LEFT]:
				gf.player.move(gf.map_objects, 'left')
			
			if pressed_keys[pygame.K_SPACE] and gf.shoot_iteration >= gf.shoot_speed:
				gf.shoot_iteration = 0
				gf.shoot(gf.player)
				gf.shouted = True


	def get_information(self=None, parse=True):
		info = self.s.recv(1024).decode(ENCODING)
		#print(info)
		if parse and ('[' in info or '{' in info):
			return json.loads(info)
		return info

	def send_information(self):
		info = {'session_id':self.session_id, 'player_data':self.player_data}
		self.s.send(utils.prepare_object_to_sending(info))

	def connect(self):
		self.s = socket.socket()
		self.s.connect(self.server)

	def disconnect(self):
		if self.s.fileno() != -1:
			self.s.shutdown(socket.SHUT_RDWR)
			self.s.close()

	def quit(self):
		self.disconnect()
		pygame.quit()
		sys.exit()




if __name__ == '__main__':
	gf = GameFunctions.GameFunctions()
	Main(gf).main(gf)