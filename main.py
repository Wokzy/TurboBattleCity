import pygame, images, GameFunctions, sys, os
from constants import *


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

	def main(self, gf):
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

		if gf.game_status == 1:
			gf.update_battle()
		elif gf.game_status == 0:
			gf.main_menu_update()

		if gf.game_status == 1:
			rm_lst = []
			for bullet in gf.bullets:
				bullet.update()
				for obj in gf.map_objects:
					if obj.__class__.__name__ == 'Wall':
						if bullet.rect.colliderect(obj.rect) or bullet.rect.x < 0 or bullet.rect.y < 0 or bullet.rect.y > HEIGHT or bullet.rect.x > WIDTH:
							rm_lst.append(bullet)
							break

			for bullet in rm_lst:
				gf.bullets.remove(bullet)

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
					gf.player = None
				else:
					gf.player.image = gf.player.death_images[1]


		if self.iterations == 3628800: # 3628800 = !10
			self.iterations = 0

	def blit_objects(self, gf):
		for obj in gf.additional_objects:
			self.screen.blit(obj.image, obj.rect)

		if gf.game_status == 1:
			if gf.player != None:
				self.screen.blit(gf.player.image, gf.player.rect)
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
				pygame.quit()
				sys.exit()
			elif event.type == pygame.MOUSEBUTTONDOWN:
				mos_pos = pygame.mouse.get_pos()
				for obj in gf.additional_objects:
					if obj.__class__.__name__ == 'Button' and obj.rect.collidepoint(mos_pos):
						obj.action(gf)
						break
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_t and gf.player != None:
					gf.player.alive = False

		if gf.game_status == 1 and gf.player != None and gf.player.alive:
			if pressed_keys[pygame.K_UP]:
				gf.player.move(gf, 'forward')
			elif pressed_keys[pygame.K_DOWN]:
				gf.player.move(gf, 'back')
			elif pressed_keys[pygame.K_RIGHT]:
				gf.player.move(gf, 'right')
			elif pressed_keys[pygame.K_LEFT]:
				gf.player.move(gf, 'left')
			if pressed_keys[pygame.K_SPACE] and gf.shoot_iteration >= gf.shoot_speed:
				gf.shoot_iteration = 0
				gf.shoot()





gf = GameFunctions.GameFunctions()
Main(gf).main(gf)