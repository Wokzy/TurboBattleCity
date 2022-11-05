import pygame
from constants import *


def get_tank():
	global TANK
	return TANK


def get_start_button():
	global START_BUTTON
	return START_BUTTON


def get_wall():
	global WALL
	return WALL


def get_river():
	global RIVER
	return RIVER


def get_grass():
	global GRASS
	return GRASS


def get_green_tank():
	global GREEN_TANK
	return GREEN_TANK


def get_red_tank():
	global RED_TANK
	return RED_TANK


def get_bullet():
	global BULLET
	return BULLET


def get_blew_tank():
	global BLEW_TANK
	return BLEW_TANK


def get_leave_session_button():
	global LEAVE_SESSION_BUTTON
	return LEAVE_SESSION_BUTTON


def get_spawn():
	global SPAWN
	return SPAWN


def get_boost_bar():
	global BOOST_BAR
	return BOOST_BAR

def get_immortality_patternts():
	global IMMORTALITY_PATTERNS
	return IMMORTALITY_PATTERNS

def get_runes():
	global RUNES
	return RUNES


def init():
	global TANK, START_BUTTON, RIVER, WALL, GRASS, GREEN_TANK, RED_TANK, BULLET, BLEW_TANK
	global LEAVE_SESSION_BUTTON, SPAWN, BOOST_BAR, IMMORTALITY_PATTERNS, RUNES

	TANK = None
	START_BUTTON = pygame.transform.scale(pygame.image.load('sprites/buttons/start_button.png'), START_BUTTON_SIZE)
	LEAVE_SESSION_BUTTON = pygame.transform.scale(pygame.image.load('sprites/buttons/leave_session_button.png'), LEAVE_SESSION_BUTTON_SIZE)
	WALL = pygame.transform.scale(pygame.image.load('sprites/blocks/wall.png'), BLOCK_SIZE)
	RIVER = pygame.transform.scale(pygame.image.load('sprites/blocks/river.png'), BLOCK_SIZE)
	SPAWN = pygame.transform.scale(pygame.image.load('sprites/blocks/spawn.png'), BLOCK_SIZE)
	GRASS = {"filled":pygame.transform.scale(pygame.image.load('sprites/blocks/grass.png'), BLOCK_SIZE), "transparent":pygame.transform.scale(pygame.image.load('sprites/blocks/transparent_grass.png'), BLOCK_SIZE)}

	GREEN_TANK = {"back":pygame.transform.scale(pygame.image.load('sprites/green_tank/tank_back.png'), TANK_SIZE),
				"forward":pygame.transform.scale(pygame.image.load('sprites/green_tank/tank_forward.png'), TANK_SIZE),
				"right":pygame.transform.scale(pygame.image.load('sprites/green_tank/tank_right.png'), TANK_SIZE),
				"left":pygame.transform.scale(pygame.image.load('sprites/green_tank/tank_left.png'), TANK_SIZE),}

	RED_TANK = {"back":pygame.transform.scale(pygame.image.load('sprites/red_tank/tank_back.png'), TANK_SIZE),
				"forward":pygame.transform.scale(pygame.image.load('sprites/red_tank/tank_forward.png'), TANK_SIZE),
				"right":pygame.transform.scale(pygame.image.load('sprites/red_tank/tank_right.png'), TANK_SIZE),
				"left":pygame.transform.scale(pygame.image.load('sprites/red_tank/tank_left.png'), TANK_SIZE),}

	IMMORTALITY_PATTERNS = {"back":pygame.transform.scale(pygame.image.load('sprites/tank_patterns/immortality_back.png'), IMMORTALITY_PATTERN_SIZE),
				"forward":pygame.transform.scale(pygame.image.load('sprites/tank_patterns/immortality_forward.png'), IMMORTALITY_PATTERN_SIZE),
				"right":pygame.transform.scale(pygame.image.load('sprites/tank_patterns/immortality_right.png'), IMMORTALITY_PATTERN_SIZE),
				"left":pygame.transform.scale(pygame.image.load('sprites/tank_patterns/immortality_left.png'), IMMORTALITY_PATTERN_SIZE),}

	BULLET = {"back":pygame.transform.scale(pygame.image.load('sprites/bullet/shot_back.png'), SHOT_SIZE),
				"forward":pygame.transform.scale(pygame.image.load('sprites/bullet/shot_forward.png'), SHOT_SIZE),
				"right":pygame.transform.scale(pygame.image.load('sprites/bullet/shot_right.png'), SHOT_SIZE),
				"left":pygame.transform.scale(pygame.image.load('sprites/bullet/shot_left.png'), SHOT_SIZE),}

	BLEW_TANK = [pygame.transform.scale(pygame.image.load('sprites/animations/tank_boom_1.png'), TANK_SIZE), pygame.transform.scale(pygame.image.load('sprites/animations/tank_boom_2.png'), TANK_SIZE)]

	BOOST_BAR = {"bar":pygame.transform.scale(pygame.image.load('sprites/yellow_bar.png'), BOOST_BAR_SIZE),
				 "background":pygame.transform.scale(pygame.image.load('sprites/grey_bar.png'), BOOST_BAR_SIZE)}

	RUNES = {
			"haste":{
					"state":pygame.transform.scale(pygame.image.load('sprites/runes/haste.png'), RUNE_SIZE)
					},
			"immortality":
					{
					"state":pygame.transform.scale(pygame.image.load('sprites/runes/immortality.png'), RUNE_SIZE)
					},
			"reveal":
					{
					"state":pygame.transform.scale(pygame.image.load('sprites/runes/reveal.png'), SQUARE_RUNE_SIZE)
					},
			}

init()