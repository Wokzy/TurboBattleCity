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

	def action(self, gf):
		if self.name == 'start_battle':
			gf.start_battle()


class Wall:
	def __init__(self, position):
		self.image = images.get_wall()
		self.rect = self.image.get_rect()

		self.rect.x = position[0]
		self.rect.y = position[1]


class River:
	def __init__(self, position):
		self.image = images.get_river()
		self.rect = self.image.get_rect()

		self.rect.x = position[0]
		self.rect.y = position[1]

class Grass:
	def __init__(self, position):
		self.images = images.get_grass()
		self.image = self.images['filled']
		self.rect = self.image.get_rect()

		self.rect.x = position[0]
		self.rect.y = position[1]



class Tank:
	def __init__(self, player, position, rotation='forward'):
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

		self.speed = TANK_SPEED

		self.alive = True
		self.death_animation_speed = FPS // 2
		self.death_animation_iteration = 0

	def move(self, gf, rotation):
		self.image = self.images[rotation]
		self.rotation = rotation

		if rotation == 'forward':
			if self.rect.y - self.speed >= 0:
				self.rect.y -= self.speed
			else: return
			for obj in gf.map_objects:
				if obj.__class__.__name__ == 'Wall' or obj.__class__.__name__ == 'River':
					if obj.rect.colliderect(self.rect):
						self.rect.y += self.speed
						return
		elif rotation == 'back':
			if self.rect.y + self.speed <= HEIGHT - TANK_SIZE[1]:
				self.rect.y += self.speed
			else: return
			for obj in gf.map_objects:
				if obj.__class__.__name__ == 'Wall' or obj.__class__.__name__ == 'River':
					if obj.rect.colliderect(self.rect):
						self.rect.y -= self.speed
						return
		elif rotation == 'right':
			if self.rect.x + self.speed <= WIDTH - TANK_SIZE[0]:
				self.rect.x += self.speed
			else: return
			for obj in gf.map_objects:
				if obj.__class__.__name__ == 'Wall' or obj.__class__.__name__ == 'River':
					if obj.rect.colliderect(self.rect):
						self.rect.x -= self.speed
						return
		elif rotation == 'left':
			if self.rect.x - self.speed >= 0:
				self.rect.x -= self.speed
			else: return
			for obj in gf.map_objects:
				if obj.__class__.__name__ == 'Wall' or obj.__class__.__name__ == 'River':
					if obj.rect.colliderect(self.rect):
						self.rect.x += self.speed
						return



class Bullet:
	def __init__(self, rotation, position):
		self.image = images.get_bullet()[rotation]
		self.rotation = rotation

		self.rect = self.image.get_rect()
		self.rect.x = position[0]
		self.rect.y = position[1]

		self.speed = BULLET_SPEED

	def update(self):
		if self.rotation == "forward":
			self.rect.y -= self.speed
		elif self.rotation == "back":
			self.rect.y += self.speed
		elif self.rotation == "right":
			self.rect.x += self.speed
		elif self.rotation == "left":
			self.rect.x -= self.speed