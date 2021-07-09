import images
from constants import *
from scripts import objects, maps


class GameFunctions:
	def __init__(self):
		self.additional_objects = []
		self.enemyes = []
		self.bullets = []
		self.grass = []

		self.shoot_speed = FPS
		self.shoot_iteration = self.shoot_speed

		self.player = None

		self.level = 1

		self.game_status = 0 # 0 - Menu; 1 - In game

		self.init_optimization()

		self.adding_enemyes_speed = FPS * 1
		self.adding_enemyes_iteration = 0


	def main_menu_update(self):
		if not self.main_menu_on:
			self.main_menu_on = True
			self.additional_objects.append(objects.Button('start_battle', images.get_start_button(), (WIDTH//2 - START_BUTTON_SIZE[0]//2, HEIGHT//2 - START_BUTTON_SIZE[1]//2), START_BUTTON_SIZE))


	def init_optimization(self):
		self.main_menu_on = False

	def start_battle(self):
		self.game_status = 1
		self.max_enemyes = self.level + 5
		self.enemyes = []
		self.additional_objects = []

		self.map_objects = []

		for line in maps.LEVELS[self.level - 1]:
			for obj in range(len(line)):
				crds = (obj*25*AVERAGE_MULTIPLYER, maps.LEVELS[self.level - 1].index(line)*25*AVERAGE_MULTIPLYER)
				if line[obj] == 'w':
					self.map_objects.append(objects.Wall(crds))
				elif line[obj] == 'r':
					self.map_objects.append(objects.River(crds))
				elif line[obj] == 'g':
					self.grass.append(objects.Grass(crds))
				elif line[obj] == 'p':
					self.player = objects.Tank(True, crds)



	def update_battle(self):
		self.shoot_iteration += 1


		'''
		if len(self.enemyes) < self.max_enemyes:
			if self.adding_enemyes_iteration >= self.adding_enemyes_speed:
				self.add_enemy()
				self.adding_enemyes_iteration = -1

		self.adding_enemyes_iteration += 1
		'''


	def shoot(self):
		if self.player.rotation == 'forward':
			self.bullets.append(objects.Bullet(self.player.rotation, (self.player.rect.center[0] - 9*AVERAGE_MULTIPLYER, self.player.rect.y - 5*AVERAGE_MULTIPLYER)))
		elif self.player.rotation == 'back':
			self.bullets.append(objects.Bullet(self.player.rotation, (self.player.rect.center[0] - 9*AVERAGE_MULTIPLYER, self.player.rect.y + 5*AVERAGE_MULTIPLYER)))
		elif self.player.rotation == 'right':
			self.bullets.append(objects.Bullet(self.player.rotation, (self.player.rect.x + 5*AVERAGE_MULTIPLYER, self.player.rect.center[1] - 9*AVERAGE_MULTIPLYER)))
		elif self.player.rotation == 'left':
			self.bullets.append(objects.Bullet(self.player.rotation, (self.player.rect.x - 5*AVERAGE_MULTIPLYER, self.player.rect.center[1] - 9*AVERAGE_MULTIPLYER)))