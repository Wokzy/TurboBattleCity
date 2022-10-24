import images
from constants import *


class Button:
	def __init__(self, name, image, position, size):
		self.image = image
		self.name = name
		self.rect = self.image.get_rect()

		self.rect.x = position[0]
		self.rect.y = position[1]

		self.size = size

	def action(self, gf, main):
		if self.name == 'start_battle':
			main.start_battle(gf)
		if self.name == 'leave_session':
			main.exit_map(gf)

class Grass:
	def __init__(self, position):
		self.images = images.get_grass()
		self.image = self.images['filled']
		self.rect = self.image.get_rect()

		self.rect.x = position[0]
		self.rect.y = position[1]

class MapObject:
	def __init__(self, image, position, destroy_bullets=False, block=True):
		self.image = image
		self.rect = self.image.get_rect()

		self.destroy_bullets = destroy_bullets
		self.block = block

		self.rect.x = position[0]
		self.rect.y = position[1]



class Tank:
	def __init__(self, player, position, rotation='forward', shoot_speed=TANK_SHOOT_SPEED, spawn_index=None):
		if player == True:
			self.images = images.get_green_tank()
		else:
			self.images = images.get_red_tank()

		self.death_images = images.get_blew_tank()

		self.rotation = rotation
		self.image = self.images[rotation]
		self.rect = self.image.get_rect()
		self.rect.x = position[0]
		self.rect.y = position[1]

		self.shoot_speed = shoot_speed
		self.shoot_iteration = shoot_speed
		self.shouted = False

		self.speed = TANK_SPEED
		self.spawn_index = spawn_index

		self.alive = True
		self.death_animation_speed = FPS // 2
		self.death_animation_iteration = 0

	def move(self, map_objects, rotation):
		self.image = self.images[rotation]
		self.rotation = rotation

		if rotation == 'forward':
			if self.rect.y - self.speed >= 0:
				self.rect.y -= self.speed
			else: return
			for obj in map_objects:
				if obj.block:
					if obj.rect.colliderect(self.rect):
						self.rect.y += self.speed
						return
		elif rotation == 'back':
			if self.rect.y + self.speed <= HEIGHT - TANK_SIZE[1]:
				self.rect.y += self.speed
			else: return
			for obj in map_objects:
				if obj.block:
					if obj.rect.colliderect(self.rect):
						self.rect.y -= self.speed
						return
		elif rotation == 'right':
			if self.rect.x + self.speed <= WIDTH - TANK_SIZE[0]:
				self.rect.x += self.speed
			else: return
			for obj in map_objects:
				if obj.block:
					if obj.rect.colliderect(self.rect):
						self.rect.x -= self.speed
						return
		elif rotation == 'left':
			if self.rect.x - self.speed >= 0:
				self.rect.x -= self.speed
			else: return
			for obj in map_objects:
				if obj.block:
					if obj.rect.colliderect(self.rect):
						self.rect.x += self.speed
						return

	def update(self, x, y, rotation, score=0, alive=True):
		self.image = self.images[rotation]
		self.rotation = rotation
		self.rect.x = x
		self.rect.y = y
		self.score = score
		self.alive = alive

		self.shoot_iteration += 1



class Bullet:
	def __init__(self, rotation, position, shooter=None):
		self.image = images.get_bullet()[rotation]
		self.rotation = rotation

		self.rect = self.image.get_rect()
		self.rect.x = position[0]
		self.rect.y = position[1]

		self.speed = BULLET_SPEED
		self.shooter = shooter

	def update(self):
		if self.rotation == "forward":
			self.rect.y -= self.speed
		elif self.rotation == "back":
			self.rect.y += self.speed
		elif self.rotation == "right":
			self.rect.x += self.speed
		elif self.rotation == "left":
			self.rect.x -= self.speed