import utils
import random

from constants import ID_HASH_SIZE, ROTATIONS


class LocalGame:
	def __init__(self, level_info, players:int):
		self.level = level_info['level']
		self.max_players = level_info['max_players']
		self.spawns = level_info['spawns']
		self.availible_spawns = [True] * len(self.spawns)

		self.player_id = None
		self.players = {}

		self.scores = {}

		if players > self.max_players:
			raise ValueError("Exceeded amount of players on map")

		#if player:
		#	self.add_player(player_id=player['player_id'], player_data=player['player_data'], self.availible_spawns)


	def set_spawn(self, player_id):
		self.players[player_id]['spawn_index'] = random.choice([i for i in range(len(self.availible_spawns)) if self.availible_spawns[i]])
		self.availible_spawns[self.players[player_id]['spawn_index']] = False

		return self.players[player_id]['spawn_index']


	def add_player(self, player_id:str, player_data=None):

		self.players[player_id] = {}
		self.scores[player_id] = 0
		spawn = self.set_spawn(player_id=player_id)

		if player_data:
			self.players[player_id] = player_data
		else:
			self.players[player_id] = self.gen_player_data(spawn, player_id)

		return spawn


	def gen_player_data(self, spawn, player_id):
		return {'address':player_id, "x":self.spawns[spawn][0], "y":self.spawns[spawn][1], "rotation":ROTATIONS[0], "status":"default",
				"shouted":0, "nickname":player_id, "spawn_index":0, 'alive':1, 'statuses':{"boost":0, "immunity":0}, 'score':self.scores[player_id],
				'killed_someone':False, 'id':player_id}


	def fill_players(self, amount):
		for i in range(amount):
			player_id = utils.gen_random_shake(ID_HASH_SIZE)
			self.add_player(player_id=player_id)
			'''
			self.players[player_id] = {}
			spawn = self.set_spawn(player_id)

			self.players[player_id] = self.gen_player_data(spawn, player_id)
			'''


	def update_players(self, gf, players:list):
		for player in players:
			data = {'address':player, 'x':gf.players[player].rect.x, 'y':gf.players[player].rect.y, 'rotation':gf.players[player].rotation,
					'status':gf.players[player].status, 'nickname':self.players[player]['nickname'], 'spawn_index':self.players[player]['spawn_index'],
					'alive':gf.players[player].alive, 'statuses':{'boost':int(gf.players[player].boost), 'immunity':gf.players[player].immunity},
					'score':self.scores[player], 'killed_someone':gf.players[player].killed_someone, 'id':player, 'shouted':gf.players[player].shouted}
			self.players[player] = data


	def process_runes(self):
		pass



