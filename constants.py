import json

GAME_NAME = 'Turbo Batlle City'
GAME_VERSION = 'v1.1'

CONFIG_FILE = 'config.json'

ENCODING = 'utf-8'

f = open(CONFIG_FILE)
data = json.load(f)
f.close()

WIDTH = int(data['WIDTH'])   # 800
HEIGHT = int(data['HEIGHT']) # 800
NICKNAME = data['NICKNAME'][:12:]
SERVER_IP = data['SERVER_IP']
SERVER_PORT = 25217

MAX_PLAYERS_ON_MAP = 8

OBJECT_MULTIPLYER_WIDTH = WIDTH // 400
OBJECT_MULTIPLYER_HEIGHT = HEIGHT // 400
AVERAGE_MULTIPLYER = (OBJECT_MULTIPLYER_WIDTH + OBJECT_MULTIPLYER_HEIGHT) // 2

FPS = 60

START_BUTTON_SIZE = (165*OBJECT_MULTIPLYER_WIDTH, 75*OBJECT_MULTIPLYER_HEIGHT)
BLOCK_SIZE = (25*OBJECT_MULTIPLYER_WIDTH, 25*OBJECT_MULTIPLYER_HEIGHT)
TANK_SIZE = (15*OBJECT_MULTIPLYER_WIDTH, 15*OBJECT_MULTIPLYER_HEIGHT)
SHOT_SIZE = (8*OBJECT_MULTIPLYER_WIDTH, 8*OBJECT_MULTIPLYER_HEIGHT)
INFO_FONT_SIZE = 10*AVERAGE_MULTIPLYER
SCORE_FONT_SIZE = 32*AVERAGE_MULTIPLYER
NICK_FONT_SIZE = 7*AVERAGE_MULTIPLYER

GAME_FONT = 'Terminus.ttf'
SYS_FONT = 'Ubuntu'

BULLET_SPEED = 7
TANK_SPEED = 2