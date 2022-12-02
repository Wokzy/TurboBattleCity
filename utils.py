import pygame
from constants import *

def prepare_object_to_sending(obj, split_data=False):
	if split_data:
		string = str(obj) + '\n'
	else:
		string = str(obj)
	return string.replace("'", '"').encode(ENCODING)


def event_handling(gf):
	pressed_keys = pygame.key.get_pressed()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			return 'quit'
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
		if (pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]):
			gf.player.turn_on_boost()

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

