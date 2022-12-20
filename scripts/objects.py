import copy
import images

from constants import *
from datetime import datetime


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
		self.player = player

		if player == True:
			self.images = images.get_green_tank()
		else:
			self.images = images.get_red_tank()

		self.death_images = images.get_blew_tank()

		self.rotation = rotation
		self.image = self.images[rotation]
		self.additional_images = {}
		self.top_additional_images = {}
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

		self.boost = False
		self.boost_timer = datetime.now()

		self.immunity = False
		self.immunity_timer = None

		self.show_nickname = True

		self.active_runes = {i:False for i in RUNES_CONFIG['runes']}
		self.killed_someone = False

	def move(self, map_objects, rotation):
		self.image = self.images[rotation]
		self.rotation = rotation
		current_speed = self.speed + int(self.boost) * (TANK_SPEED_BOOST_MULTIPLYER - 1)

		if rotation == 'forward':
			if self.rect.y - current_speed >= 0:
				self.rect.y -= current_speed 
			else: return
			for obj in map_objects:
				if obj.block:
					if obj.rect.colliderect(self.rect):
						self.rect.y += current_speed
						return
		elif rotation == 'back':
			if self.rect.y + current_speed <= HEIGHT - TANK_SIZE[1]:
				self.rect.y += current_speed
			else: return
			for obj in map_objects:
				if obj.block:
					if obj.rect.colliderect(self.rect):
						self.rect.y -= current_speed
						return
		elif rotation == 'right':
			if self.rect.x + current_speed <= WIDTH - TANK_SIZE[0]:
				self.rect.x += current_speed
			else: return
			for obj in map_objects:
				if obj.block:
					if obj.rect.colliderect(self.rect):
						self.rect.x -= current_speed
						return
		elif rotation == 'left':
			if self.rect.x - current_speed >= 0:
				self.rect.x -= current_speed
			else: return
			for obj in map_objects:
				if obj.block:
					if obj.rect.colliderect(self.rect):
						self.rect.x += current_speed
						return


	def update_boost_images(self):
		if 'boost' not in self.additional_images or self.additional_images['boost'] == []:
			self.generate_boost_images()

		for i in range(1, len(self.additional_images['boost'])):
			self.additional_images['boost'][-i] = self.additional_images['boost'][-i-1]
			self.additional_images['boost'][-i]['image'].set_alpha(self.min_shadow_alpha + self.shadows_alpha_range*(i-1))

		self.additional_images['boost'][0] = {'image':copy.copy(self.image), 'position':(self.rect.x, self.rect.y)}


	def general_update(self, runes=None):
		self.killed_someone = False
		if self.boost:
			#if 'boost' not in self.additional_images:
			#	self.turn_on_boost(force = True)

			#print(self.additional_images)

			self.update_boost_images()
			if self.player and runes[BOOST_RUNE_NAME] == False and (datetime.now() - self.boost_timer).total_seconds() > BOOST_DURATION:
				self.turn_off_boost()


		elif 'boost' in self.additional_images:
			del self.additional_images['boost']

		if self.immunity:
			self.top_additional_images['immunity'] = {'image':images.get_immortality_patternts()[self.rotation], 'position':(self.rect.x, self.rect.y)}
			if self.player and runes[IMMUNITY_RUNE_NAME] != False:
				return
			if self.immunity_timer != None and (datetime.now() - self.immunity_timer).total_seconds() >= IMMUNITY_DURATION:
				self.immunity_timer = None
				self.immunity = False
		elif 'immunity' in self.top_additional_images:
			del self.top_additional_images['immunity']



	def update(self, x, y, rotation, score=0, alive=True, boost=..., immunity=False):
		self.image = self.images[rotation]
		self.rotation = rotation
		self.rect.x = x
		self.rect.y = y
		self.score = score
		self.alive = alive
		self.immunity = immunity
		self.killed_someone = False

		if self.boost != Ellipsis:
			if not self.boost and boost:
				self.turn_on_boost()
			elif self.boost and not boost:
			#self.boost = boost
				self.turn_off_boost()
			self.general_update()

		self.shoot_iteration += 1

	def process_death(self):
		if self.alive == False:
			self.death_animation_iteration += 1

			if self.death_animation_iteration >= self.death_animation_speed * len(self.death_images):
				return True
			else:
				self.image = self.death_images[self.death_animation_iteration // self.death_animation_speed]

		return False

	def turn_on_boost(self):
		if self.player:
			if self.boost or (datetime.now() - self.boost_timer).total_seconds() < BOOST_RECOVERY_DURATION:
				return

			self.boost_timer = datetime.now()

		self.boost = True
		self.generate_boost_images()


	def generate_boost_images(self):
		amount_of_shadows = 6
		self.min_shadow_alpha = 0
		self.shadows_alpha_range = (255 - self.min_shadow_alpha) / amount_of_shadows
		images_name = 'boost'

		self.additional_images[images_name] = []

		for i in range(amount_of_shadows + 1):
			img = {'image':copy.copy(self.image), 'position':(self.rect.x, self.rect.y)}
			img['image'].set_alpha(255 - self.shadows_alpha_range * i)
			self.additional_images[images_name].append(img)


	def turn_off_boost(self):
		if self.player:
			self.boost_timer = datetime.now()

		self.boost = False
		self.additional_images['boost'] = []


	def set_immunity(self):
		self.immunity_timer = datetime.now()
		self.immunity = True




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