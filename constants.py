import json

GAME_NAME = 'Turbo Batlle City'
GAME_VERSION = 'v0.1.0-alpha'

CONFIG_FILE = 'config.json'

ENCODING = 'utf-8'

f = open(CONFIG_FILE)
data = json.load(f)
f.close()

WIDTH = 800
HEIGHT = 800
MAX_NICKNAME_LENTH = 12
NICKNAME = data['NICKNAME'][:MAX_NICKNAME_LENTH:]
SERVER_IP = data['SERVER_IP']
SERVER_PORT = 25217

MAX_PLAYERS_ON_MAP = 8

OBJECT_MULTIPLYER_WIDTH = WIDTH // 400
OBJECT_MULTIPLYER_HEIGHT = HEIGHT // 400
AVERAGE_MULTIPLYER = (OBJECT_MULTIPLYER_WIDTH + OBJECT_MULTIPLYER_HEIGHT) // 2

FPS = 120
TICK_RATE = 64
MOVEMENT_TICKS = FPS / 60
BULLET_SPEED = (3.5*AVERAGE_MULTIPLYER) / MOVEMENT_TICKS
TANK_SPEED = (1*AVERAGE_MULTIPLYER) / MOVEMENT_TICKS
TANK_SHOOT_SPEED = FPS
AMMUNITION_SIZE = 5
AMMUNITION_RELOAD_SPEED = 4.75 # Float
IMMUNITY_DURATION = 0#1.75
DEATH_DURATION = 2.0

START_BUTTON_SIZE = (165*OBJECT_MULTIPLYER_WIDTH, 75*OBJECT_MULTIPLYER_HEIGHT)
BLOCK_SIZE = (25*OBJECT_MULTIPLYER_WIDTH, 25*OBJECT_MULTIPLYER_HEIGHT)
LEAVE_SESSION_BUTTON_SIZE = BLOCK_SIZE
TANK_SIZE = (15*OBJECT_MULTIPLYER_WIDTH, 15*OBJECT_MULTIPLYER_HEIGHT)
SHOT_SIZE = (8*OBJECT_MULTIPLYER_WIDTH, 8*OBJECT_MULTIPLYER_HEIGHT)
INFO_FONT_SIZE = 10*AVERAGE_MULTIPLYER
SCORE_FONT_SIZE = 32*AVERAGE_MULTIPLYER
NICK_FONT_SIZE = 7*AVERAGE_MULTIPLYER
AMMUNITION_FONT_SIZE = 28*AVERAGE_MULTIPLYER

GAME_FONT = 'Terminus.ttf'
SYS_FONT = 'Ubuntu'

CRASH_LOGGING_DIRECTORY = 'crash_logs'
