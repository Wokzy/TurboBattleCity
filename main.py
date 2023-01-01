import pygame
import GameFunctions

from constants import *
from engine import engine as engine_lib
from scripts import player_interaction, maps
from engine import network_handler, local_game


pygame.init()

global clock
clock = pygame.time.Clock()

def player():
	gf = GameFunctions.GameFunctions()

	#nwh = network_handler.NetworkHandler()
	#nwh.start()

	level_id = 1
	players = 4
	spawns = gf.get_coords(level=level_id, obj='s')
	max_players = len(spawns)
	localgame = local_game.LocalGame(level_info={'level':level_id, 'max_players':max_players, 'spawns':spawns}, players=players)
	localgame.fill_players(players-1)

	settings = {
				"network":False,
				#"network_handler":nwh,
				"localgame":localgame,
				"level":level_id,
				"player":True,
				"screen":{"caption":GAME_NAME}
	}

	engine = engine_lib.run(gf = gf, settings_set=settings)

	while True:
		engine.game_loop(gf)
		#engine.network_handler.update()
		if player_interaction.event_handling(gf) == 'quit':
			engine.quit()
			break

		#print(engine.network_handler.player_data)

		clock.tick(FPS) #FPS

player()
