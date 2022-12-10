import pygame
import engine as engine_lib
import GameFunctions

from constants import *
from scripts import player_interaction


pygame.init()

global clock
clock = pygame.time.Clock()

def player():
	gf = GameFunctions.GameFunctions()

	nwh = engine_lib.NetworkHandler()

	settings = {
				"network":True,
				"network_handler":nwh,
				"player":True,
				"screen":{"caption":GAME_NAME}
	}

	engine = engine_lib.run(gf = gf, settings_set=settings)

	while True:
		engine.game_loop(gf)
		engine.network_handler.update()
		if player_interaction.event_handling(gf) == 'quit':
			engine.quit()
			break

		clock.tick(FPS)

player()
